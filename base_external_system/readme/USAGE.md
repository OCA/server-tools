## Implementation

The credentials for systems are stored in the `external.system` model,
and are to be configured by the user. This model is the unified
interface for the underlying adapters.

### Using the Interface

Given an `external.system` singleton called `external_system`, you would
do the following to get the underlying system client:

``` python
with external_system.client() as client:
    client.do_something()
```

The client will be destroyed once the context has completed. Destruction
takes place in the adapter's `external_destroy_client` method.

The only unified aspect of this interface is the client connection
itself. Other more opinionated interface/adapter mechanisms can be
implemented in other modules, such as the file system interface in
[OCA/server-tools/external_file_location](https://github.com/OCA/server-tools/tree/9.0/external_file_location).

### Creating an Adapter

Modules looking to add an external system adapter should inherit the
`external.system.adapter` model and override the following methods:

- `external_get_client`: Returns a usable client for the system
- `external_destroy_client`: Destroy the connection, if applicable. Does
  not need to be defined if the connection destroys itself.
