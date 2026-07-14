# MatchVision AI - Brain

Purpose: compact, implementation-grounded context for future contributors and agents. Update only affected files when code changes.

## Index

| File | Use when |
| --- | --- |
| [current-state.md](current-state.md) | Understanding the implemented architecture, flow, files, dependencies, and gaps. |
| [roadmap.md](roadmap.md) | Implementing the next commit-sized milestone. |
| [conventions.md](conventions.md) | Adding code, tests, runtime files, APIs, or configuration. |

## Fast start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Entry point: `app.py`. Configuration root: `config.py`. Current state: Phase 1 foundation only; no video, API, database, authentication, or AI pipeline is implemented yet.
