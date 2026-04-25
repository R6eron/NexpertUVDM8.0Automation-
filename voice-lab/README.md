# Voice Lab — Native Termux (ElevenLabs IVC + OpenVoice)

A runnable toolkit that operationalizes the workflow described in
[`docs/openvoice-elevenlabs-termux-voice-cloning-guide.pdf`](../docs/openvoice-elevenlabs-termux-voice-cloning-guide.pdf).

**Constraints:**

- Native Termux on Android only. No `proot`, `chroot`, Docker, or remote-GPU paths.
- ElevenLabs Instant Voice Clone (IVC) is the reliable end-to-end path.
- OpenVoice is supported as a native dependency-check / setup path with guardrails;
  it will tell you exactly what fails (typically PyTorch wheels), instead of pretending.

## Files

| File | Purpose |
| --- | --- |
| `setup_termux_voice_lab.sh` | Install Termux packages, create venv, install the ElevenLabs SDK, write `.env.example`. |
| `record_sample.sh` | Record a mic sample via `termux-microphone-record`. |
| `prepare_audio.sh` | FFmpeg-normalize samples into ElevenLabs-friendly MP3 and OpenVoice-friendly WAV. |
| `create_ivc.py` | Upload samples and create an Instant Voice Clone, save voice id locally. |
| `speak_ivc.py` | Generate speech from a saved voice id and write an MP3. |
| `play_output.sh` | Play audio with `mpv`/`ffplay`, optional `termux-tts-speak` cue. |
| `multilingual_test.py` | EN/ES/FR/DE smoke test through the cloned voice. |
| `openvoice_native_check.sh` | Probe / best-effort install OpenVoice + MeloTTS natively, with guardrails. |
| `smoke_test.sh` | Validate tools, venv, env, and (optionally) API readiness. |

## Operational flow

```bash
cd voice-lab

# 1) One-time bootstrap (idempotent).
bash setup_termux_voice_lab.sh

# 2) Configure secrets. Never commit .env.
cp .env.example .env
$EDITOR .env   # add ELEVENLABS_API_KEY=...

# 3) Record three samples (~20s each, varied intonation).
bash record_sample.sh 20 samples/sample_01.m4a
bash record_sample.sh 20 samples/sample_02.m4a
bash record_sample.sh 20 samples/sample_03.m4a

# 4) Normalize samples.
bash prepare_audio.sh samples prepared

# 5) Create the IVC. The voice id is saved to config/voice.json.
.venv/bin/python create_ivc.py --name "MyVoice" prepared/*.mp3

# 6) Speak.
.venv/bin/python speak_ivc.py --text "Hello from Termux"

# 7) Listen.
bash play_output.sh "$(ls -t output/speak_*.mp3 | head -n1)"

# 8) Multilingual smoke test.
.venv/bin/python multilingual_test.py

# 9) Optional: probe native OpenVoice support.
bash openvoice_native_check.sh           # report only
bash openvoice_native_check.sh --install # best-effort install (often fails on torch)

# Validate the environment any time:
bash smoke_test.sh        # local checks
bash smoke_test.sh --api  # also pings ElevenLabs /v1/user
```

## Notes

- All scripts use `set -euo pipefail`, quote paths, and avoid hardcoded API keys.
- Secrets live in `.env` (gitignored). Voice ids land in `config/voice.json`.
- Generated audio (`samples/`, `prepared/`, `output/`) and venvs are gitignored.
- `record_sample.sh` requires the **Termux:API** Android app installed *and*
  microphone permission granted to it. Without that, the command fails with a
  clear error rather than hanging.
- `openvoice_native_check.sh` will tell you when PyTorch can't be installed
  natively on Android/aarch64. The supported fallback in this toolkit is
  ElevenLabs IVC — we do **not** silently switch to proot/Docker.

## Reference

- Full walkthrough: `docs/openvoice-elevenlabs-termux-voice-cloning-guide.pdf`
- ElevenLabs Python SDK: <https://github.com/elevenlabs/elevenlabs-python>
- OpenVoice: <https://github.com/myshell-ai/OpenVoice>
- MeloTTS: <https://github.com/myshell-ai/MeloTTS>
