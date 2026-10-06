# modkit

A minimal, reproducible version of a ports-and-adapters module system used in
a production backend (de-identified: nothing here is specific to that app).

One interface per capability ("port"), one folder per capability holding
interchangeable implementations ("adapters"), a generic `Registry[T]` that
selects exactly one adapter per category from settings, and a
`run_preflight()` that starts and health-checks everything before the app
serves traffic.

| Layer | File | Job |
|---|---|---|
| Base contract | `interfaces/module.py` | `Module`, `Startable`, `ServiceHealth`, `HealthCheck`, `HealthProbe` |
| Port | `interfaces/cache.py`, `interfaces/vault.py` | Capability ABC + `category`; optional extension ports (`RawClientProvider`, `DynamicCredentialsCapable`) |
| Adapter | `modules/<category>/*.py` | Concrete impl; the filename *is* the registry name |
| Composition | `modules/registry.py`, `modules/__init__.py`, `modules/preflight.py`, `environments.py`, `settings.py` | Discover, select, validate, start |
| Demo | `app.py` | Business logic that only ever sees a port, never a backend name |

## Categories in this example

| Category | Port | Adapter |
|---|---|---|
| `cache` | `Cache` | `REDIS` (redis-py) |
| `vault` | `Vault` | `HASHICORP` (HashiCorp Vault) |

Both adapters need a reachable server. Adapters are only imported the moment
a registry actually resolves one (`registry.default`), never eagerly.

## Run

```bash
uv sync

# quick throwaway servers for the demo
docker run -d --name modkit-redis -p 6379:6379 redis:7-alpine
docker run -d --name modkit-vault -p 8200:8200 --cap-add=IPC_LOCK \
  -e VAULT_DEV_ROOT_TOKEN_ID=root-token \
  -e VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200 \
  hashicorp/vault:1.17

VAULT_TOKEN=root-token CACHE_BACKEND=REDIS VAULT_BACKEND=HASHICORP \
  uv run python -m modkit.app

# or via a deployment profile instead of explicit backend names
VAULT_TOKEN=root-token DEPLOYMENT_ENVIRONMENT=PRODUCTION \
  uv run python -m modkit.app

# preflight failure demo: point at nothing
uv run python -m modkit.app

# invalid selection demo
CACHE_BACKEND=MONGO VAULT_BACKEND=HASHICORP uv run python -m modkit.app

docker rm -f modkit-redis modkit-vault
```

## The pattern, in short

1. **A module is just a file.** Drop `modules/cache/memcached.py` in and
   `MEMCACHED` is a selectable backend - the registry discovers it by
   filename, no registration step.
2. **Nominal typing.** Business code is written against `Cache`, never
   `Redis`; `cache_registry.default` returns *something* that satisfies
   the port.
3. **Capabilities, not backend branching.** Extra behaviour some adapters
   support (`RawClientProvider.raw_client()`,
   `DynamicCredentialsCapable.dynamic_credentials()`) lives on separate
   mixins, checked with `isinstance`, instead of `if backend == "redis"`.
4. **Preflight gates startup.** `run_preflight()` starts and health-checks
   every selected module before the app does anything else; a single
   unreachable dependency fails fast with a clear message.
5. **Deployment profiles lock combinations.** `DEPLOYMENT_ENVIRONMENT`
   pins every `*_backend` to a known-good set (`environments.py`), so a
   restricted environment can't accidentally be configured with a backend
   it isn't allowed to use.
