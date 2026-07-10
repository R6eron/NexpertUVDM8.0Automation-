# TERMUX_METHOD

When paste corruption appears in Termux, stop heredocs and use safe-write methods only.

Rules:
- Default to shell-first solutions.
- Prefer one-shot copy-pasteable patches.
- Avoid raw multiline pasted code when wrapping/corruption appears.
- Prefer line-array writers, base64 decode, or local source files already on disk.
- Inspect, test, iterate, then deliver one complete overwrite.
- Preserve ~/.bashrc persistence, UVDM continuity, dynamic voice, and mobile-friendly output.
