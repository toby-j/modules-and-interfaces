# modkit

modkit is an example, minimal reproducible example of a modular approach to service architecture in Python:

An example, with the Cache interface:
```
                  main.py
                     │
                     │ 
                     ▼
            ┌───────────────────────┐
            │   Cache (interface)   │  interfaces/cache.py
            └───────────────────────┘
                     ▲
                     │ returns something that satisfies the port
                     │
            ┌──────────────────┐        
            │  cache_registry  │◀───────  .env CACHE_BACKEND
            │   Registry[T]    │        
            └──────────────────┘
                     │
                     │ discovers by filename, imports lazily on .default
                     ▼
              modules/cache/
              ├── redis.py      -> class Redis(Cache):
                                         ... redis logic that satisfies the Cache interface
                     │
                     │ In the application code (outside of this system)
                     ▼ 
           cache = cache_registry.default  <-- returns a Cache instance (with Redis working behind each of Cache's abstract classes)                    
```

- **Nominal Typing** business code is written against a strictly defined interface, which can have many different modules (Redis, CosmosDB) attached.
- **Simplistic registry design** A module (Redis) is attached to an interface (Cache) which is managed by a single registry. Importing is just 'cache_registry.default'.
- **Preflight health checks** every selected module can be easily health-checked before usage
- **Modules are just files** to create a new modules, you just simply create a new file and satisfy the interface you want your module to attach to.

---

## Prerequisites

1. [UV](https://docs.astral.sh/uv/getting-started/installation/)
2. Python (tested on 3.14 and on MacOS)
3. Docker

## Setup

1. Install the dependencies and create the virtual environment
```shell
uv sync
```

2. Spin up the docker containers

```shell
docker compose up
```

This will create a redis, postgres and a hashicorp vault container on your local machine.

## Usage

To run the entrypoint:

```shell
cd modkit
uv run main.py
```

You should see that each module is registered, the pre-flight checks passed and a report of their health checks.

### Adding a new module

This architecture is designed to be easily extended on and different software projects.

1. Create a new folder in `modules` and a file inside, with the name of your new module.
2. Inherit the interface, such as Cache and implement each of the required abstract methods, including the health check.
3. If it's for an existing interface, edit or create the environment variables <interface_backend> and make sure the registry is created in `modules/__init__.py`.
4. Optional: `run_preflight()` to check that your new module is imported and the health_check passes.
4. You're now ready to use your new module in your codebase, by importing `<inteface>_registry.default` 🎉

### Adding an interface

Each interface is a set of rules we can use to abstract away complex logic of individual services, like Redis, CosmosDB, MongoDB etc..
Often, the main application code needs to perform the same task no matter what service is configured on the backend.

The interface definition is what is exposed to the main codebase through the registry, so you define your functions and properties that it will need to use.

1. Create a new file in `modkit/interfaces` and create a class named your new interface. It must import the Module class, which every module must implement.
2. Decide and create your abstract methods. This will depend on what your application needs to do using these services.
3. We now need to give the new interface a registry so the core application can use it. Add a line to `modules/__init__.py` for example:

```python
<new_interface>_registry: Registry[<NewInterface>] = Registry(<NewModule>, _settings.<NewModule>_backend)
```
4. This can now be imported using `<new_interface>_registry.default` 🎉
