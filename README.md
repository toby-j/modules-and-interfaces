# modkit

A minimal, reproducible version of the module + infrastructure pattern in
[`desdigital/modkit`](https://github.com/desdigital/modkit/tree/feature/modkit-s/backend/src/modkit)
(`backend/src/modkit`).

Ports and adapters with filesystem-based discovery: one interface per
capability, one folder per capability holding interchangeable adapters, a
generic `Registry[T]` that selects exactly one per category from typed
settings, and a `run_preflight()` that starts and health-checks everything
before the app serves traffic.

| Layer | File | Job |
|---|---|---|
| Base contract | `interfaces/module.py` | `Module`, `Startable`, `ServiceHealth`, `HealthProbe` |
| Port | `interfaces/cache.py` | Capability ABC + `category`; optional extension ports |
| Adapter | `modules/cache/*.py` | Concrete impl; filename becomes the registry name |
| Composition | `modules/registry.py`, `modules/__init__.py`, `modules/preflight.py`, `environments.py` | Discover, select, validate, start |

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

DEPLOYMENT_ENVIRONMENT=LOCAL  python -m modkit.app   # -> MEMORY
DEPLOYMENT_ENVIRONMENT=SECURE python -m modkit.app   # -> FAKEREDIS
CACHE_BACKEND=MEMORY          python -m modkit.app   # explicit, no profile

# preflight failure demo
DEPLOYMENT_ENVIRONMENT=SECURE FAKEREDIS_UNREACHABLE=true python -m modkit.app

# invalid selection demo
CACHE_BACKEND=MONGO python -m modkit.app
