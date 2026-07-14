# Engineering Conventions

## Boundaries

- Keep `app.py` orchestration/UI-first; move domain logic into `modules/` and external calls into `services/`.
- Put reusable, dependency-light helpers in `utils/`.
- Read paths and application constants from `config.py`; do not use machine-specific absolute paths.
- Runtime files belong in `input/` or `output/`, never in source control.
- Add a focused test with each new deterministic module.

## Integration rules

- External APIs use a service interface, timeouts, explicit error mapping, and environment-backed secrets.
- Video/audio operations must surface FFmpeg failures in user-readable form.
- Long processing must report Streamlit progress and clean temporary artifacts on success/failure.
- Model-heavy optional features remain isolated and must not block core highlight generation.

## Documentation sync

After a change, update only the relevant brain file: architecture/flow -> `current-state.md`; next scope/status -> `roadmap.md`; engineering rules -> `conventions.md`; index changes -> `brain.md`.
