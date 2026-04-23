#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import mimetypes
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import requests

LOGGER = logging.getLogger("elevenlabs_voice_notes_pipeline_v2")
SUPPORTED_AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".webm", ".mp4"}
TEXT_AUDIO_HINTS = {".log", ".txt", ".md", ""}
DEFAULT_STT_MODEL = "scribe_v1"
DEFAULT_TTS_MODEL = "eleven_multilingual_v2"
ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"


@dataclass
class FileTask:
    source: Path
    transcript_text: str
    transcript_source: str
    original_audio: Optional[Path]


@dataclass
class CloneSample:
    source: Path
    normalized: Path
    duration_seconds: float
    size_bytes: int


class RetryableClient:
    def __init__(self, api_key: str, retries: int = 4, backoff: float = 2.0, timeout: int = 600):
        self.retries = retries
        self.backoff = backoff
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"xi-api-key": api_key})

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        last_error = None
        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise requests.HTTPError(f"retryable status {response.status_code}", response=response)
                response.raise_for_status()
                return response
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as exc:
                last_error = exc
                if attempt == self.retries:
                    break
                sleep_for = self.backoff ** (attempt - 1)
                LOGGER.warning("Request failed on attempt %s/%s: %s; retrying in %.1fs", attempt, self.retries, exc, sleep_for)
                time.sleep(sleep_for)
        raise RuntimeError(f"API request failed after {self.retries} attempts: {last_error}")


class ElevenLabsClient:
    def __init__(self, api_key: str, retries: int = 4, backoff: float = 2.0):
        self.http = RetryableClient(api_key=api_key, retries=retries, backoff=backoff)

    def transcribe(self, audio_path: Path, model_id: str = DEFAULT_STT_MODEL, language_code: Optional[str] = None) -> str:
        mime = mimetypes.guess_type(audio_path.name)[0] or "application/octet-stream"
        data = {"model_id": model_id}
        if language_code:
            data["language_code"] = language_code
        with audio_path.open("rb") as fh:
            files = {"file": (audio_path.name, fh, mime)}
            response = self.http.request("POST", f"{ELEVENLABS_BASE}/speech-to-text", data=data, files=files)
        text = response.json().get("text", "").strip()
        if not text:
            raise RuntimeError(f"No transcript text returned for {audio_path}")
        return text

    def create_voice_clone(self, name: str, sample_paths: List[Path], description: str, labels: Optional[dict] = None) -> str:
        data = {"name": name, "description": description}
        if labels:
            data["labels"] = json.dumps(labels)
        files = []
        handles = []
        try:
            for sample in sample_paths:
                fh = sample.open("rb")
                handles.append(fh)
                mime = mimetypes.guess_type(sample.name)[0] or "application/octet-stream"
                files.append(("files", (sample.name, fh, mime)))
            response = self.http.request("POST", f"{ELEVENLABS_BASE}/voices/add", data=data, files=files)
            voice_id = response.json().get("voice_id")
            if not voice_id:
                raise RuntimeError("Voice clone creation returned no voice_id")
            return voice_id
        finally:
            for fh in handles:
                fh.close()

    def synthesize(self, text: str, voice_id: str, output_path: Path, model_id: str = DEFAULT_TTS_MODEL) -> None:
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.38,
                "similarity_boost": 0.92,
                "style": 0.62,
                "use_speaker_boost": True,
            },
        }
        response = self.http.request(
            "POST",
            f"{ELEVENLABS_BASE}/text-to-speech/{voice_id}",
            json=payload,
            headers={"Accept": "audio/mpeg"},
        )
        output_path.write_bytes(response.content)


def load_env(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._") or "untitled"


def is_audio_file(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_AUDIO_EXTS


def discover_inputs(voice_notes_dir: Path) -> List[Path]:
    if not voice_notes_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {voice_notes_dir}")
    files = [p for p in voice_notes_dir.iterdir() if p.is_file()]
    accepted = []
    for p in files:
        suffix = p.suffix.lower()
        if is_audio_file(p):
            accepted.append(p)
        elif suffix in TEXT_AUDIO_HINTS or p.name.lower() in {"xlm.log", "xlm_mode_note"}:
            accepted.append(p)
    return sorted(accepted)


def run_ffmpeg(cmd: List[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def ffprobe_duration(audio_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def normalize_audio(source: Path, normalized_dir: Path) -> Path:
    normalized_dir.mkdir(parents=True, exist_ok=True)
    target = normalized_dir / f"{sanitize_filename(source.stem)}.wav"
    cmd = [
        "ffmpeg", "-y", "-i", str(source),
        "-af", "highpass=f=70,lowpass=f=12000,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ac", "1", "-ar", "44100", str(target)
    ]
    run_ffmpeg(cmd)
    return target


def select_clone_samples(audio_files: List[Path], normalized_dir: Path, max_samples: int, min_duration: float = 15.0) -> List[CloneSample]:
    samples: List[CloneSample] = []
    for audio in audio_files:
        try:
            normalized = normalize_audio(audio, normalized_dir)
            duration = ffprobe_duration(normalized)
            size_bytes = normalized.stat().st_size
            if duration >= min_duration:
                samples.append(CloneSample(source=audio, normalized=normalized, duration_seconds=duration, size_bytes=size_bytes))
        except Exception as exc:
            LOGGER.warning("Skipping clone candidate %s due to normalization/probe failure: %s", audio, exc)
    ranked = sorted(samples, key=lambda s: (s.duration_seconds, s.size_bytes), reverse=True)
    return ranked[:max_samples]


def extract_text_from_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def maybe_pair_original_audio(text_path: Path, pool: List[Path]) -> Optional[Path]:
    stem = text_path.stem.lower()
    for audio in pool:
        if audio.stem.lower() == stem:
            return audio
    return None


def build_tasks(client: ElevenLabsClient, inputs: List[Path], language_code: Optional[str]) -> List[FileTask]:
    audio_files = [p for p in inputs if is_audio_file(p)]
    tasks: List[FileTask] = []
    for path in inputs:
        if is_audio_file(path):
            transcript = client.transcribe(path, language_code=language_code)
            tasks.append(FileTask(source=path, transcript_text=transcript, transcript_source="stt", original_audio=path))
        else:
            text = extract_text_from_file(path)
            if not text:
                LOGGER.warning("Skipping empty text-like file: %s", path)
                continue
            tasks.append(FileTask(source=path, transcript_text=text, transcript_source="text", original_audio=maybe_pair_original_audio(path, audio_files)))
    return tasks


def write_side_by_side_outputs(task: FileTask, cloned_audio: Path, task_dir: Path) -> None:
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "transcript.txt").write_text(task.transcript_text, encoding="utf-8")
    metadata = {
        "source": str(task.source),
        "transcript_source": task.transcript_source,
        "original_audio": str(task.original_audio) if task.original_audio else None,
        "cloned_audio": str(cloned_audio),
    }
    (task_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    if task.original_audio and task.original_audio.exists():
        shutil.copy2(task.original_audio, task_dir / f"original{task.original_audio.suffix.lower()}")
    shutil.copy2(cloned_audio, task_dir / "cloned.mp3")


def check_binary(name: str) -> None:
    if shutil.which(name) is None:
        raise EnvironmentError(f"Required binary not found in PATH: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Repo-hardened ElevenLabs voice-note pipeline")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--input-dir", default="voice_notes")
    parser.add_argument("--output-dir", default="processed_voice_notes")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--clone-name", default="Nexpert UVDM Digital Twin")
    parser.add_argument("--clone-description", default="Professional Voice Clone trained from normalized clean samples to capture cadence, style, and delivery.")
    parser.add_argument("--max-clone-samples", type=int, default=6)
    parser.add_argument("--min-clone-duration", type=float, default=15.0)
    parser.add_argument("--language-code", default=None)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--backoff", type=float, default=2.0)
    parser.add_argument("--keep-normalized", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    configure_logging(args.verbose)
    repo_root = Path(args.repo_root).expanduser().resolve()
    load_env(repo_root / args.env_file)
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise EnvironmentError("ELEVENLABS_API_KEY not found in environment or .env file")

    check_binary("ffmpeg")
    check_binary("ffprobe")

    input_dir = (repo_root / args.input_dir).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    normalized_dir = output_dir / "_normalized_clone_samples"
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = discover_inputs(input_dir)
    if not inputs:
        raise RuntimeError(f"No compatible inputs found in {input_dir}")

    audio_inputs = [p for p in inputs if is_audio_file(p)]
    if not audio_inputs:
        raise RuntimeError("No audio files found; Professional Voice Clone requires audio samples")

    clone_samples = select_clone_samples(audio_inputs, normalized_dir, args.max_clone_samples, args.min_clone_duration)
    if not clone_samples:
        raise RuntimeError("No valid clone samples survived normalization and duration filters")

    LOGGER.info("Selected clone samples: %s", ", ".join(s.source.name for s in clone_samples))
    client = ElevenLabsClient(api_key=api_key, retries=args.retries, backoff=args.backoff)
    voice_id = client.create_voice_clone(
        name=args.clone_name,
        sample_paths=[s.normalized for s in clone_samples],
        description=args.clone_description,
        labels={"project": "NexpertUVDM-Automation", "pipeline": "voice_notes_v2", "style": "professional"},
    )

    tasks = build_tasks(client, inputs, args.language_code)
    manifest_items = []
    for task in tasks:
        task_dir = output_dir / sanitize_filename(task.source.stem)
        cloned_path = task_dir / "cloned.mp3"
        task_dir.mkdir(parents=True, exist_ok=True)
        client.synthesize(task.transcript_text, voice_id=voice_id, output_path=cloned_path)
        write_side_by_side_outputs(task, cloned_path, task_dir)
        manifest_items.append({
            "source": str(task.source.relative_to(repo_root)),
            "task_dir": str(task_dir.relative_to(repo_root)),
            "transcript_source": task.transcript_source,
        })
        LOGGER.info("Processed %s", task.source.name)

    manifest = {
        "voice_id": voice_id,
        "clone_samples": [
            {
                "source": str(s.source.relative_to(repo_root)),
                "normalized": str(s.normalized.relative_to(repo_root)),
                "duration_seconds": s.duration_seconds,
                "size_bytes": s.size_bytes,
            }
            for s in clone_samples
        ],
        "items": manifest_items,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if not args.keep_normalized and normalized_dir.exists():
        shutil.rmtree(normalized_dir)

    LOGGER.info("Finished successfully -> %s", output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
