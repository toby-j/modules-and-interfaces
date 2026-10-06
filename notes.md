# Modules and interfaces architecture in Python

While working on a project, I've been tasked to take a monolith, azure focused repository and convert for use in an offline environment.

This challenge was further complicated with the involvement of two workstreams, one for the online and one for the offline environment.

There was a quick consensus that we needed a modular style of architecture, but other considerations such as the impact on the online team, scalability, testing etc.. quickly came into the picture.

In this document, I propose an interface and module pattern which has the following features:

- Creating a module is just creating a file
- Modules are lazily imported
- Standardised health checks
- Nominal typing
- Additional interface capabilities (Startable, DynamicCredentialsCapable)
- Initialisation profiles

# Registry

There's a single registry which is what the core application interacts with then it needs to use a module.

`modules/__init__.py`
```python
cache_registry: Registry[Cache] = Registry(Cache, _settings.cache_backend)
```

`_settings.cache_backend` is a name for a module. For example, "REDIS".

`Cache` is the interface. Which defines a list of abstract functions and properties that a `Cache` module must implement. Such as `get()` and `set()`.

If the core app needs to call on a cache module, it simply uses:

```python
cache_registry.default
```

This will be of type `Cache`, through nominal typing.

# Interfaces

Every module must implement an interface, this allows
