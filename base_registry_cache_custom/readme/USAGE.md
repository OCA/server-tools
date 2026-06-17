If you need to create a custom cache, create a new module and:

- add this module as its dependency
- add a `post_load` hook like this:

```python
from odoo.addons.base_registry_cache_custom.registry import add_custom_cache


def post_load():
    add_custom_cache(name="my_cache", count=256)
```

If you make use of multiple caches, and some of them should be invalidated when another
one gets invalidated itself, use the `depends_on_caches` argument:

```python
from odoo.addons.base_registry_cache_custom.registry import add_custom_cache


def post_load():
    add_custom_cache(name="my_cache_1", count=256)
    add_custom_cache(name="my_cache_2", count=128, depends_on_caches=["my_cache_1"])
```

You can also add sub-caches, which can be declared using dotted names, and will be
invalidated only when one of their dependency caches are invalidated:

```python
from odoo.addons.base_registry_cache_custom.registry import add_custom_cache


def post_load():
    add_custom_cache(name="my_cache", count=256)
    add_custom_cache(name="my_cache.subcache", count=128, depends_on_caches=["my_cache"], allows_direct_invalidation=False)
```
