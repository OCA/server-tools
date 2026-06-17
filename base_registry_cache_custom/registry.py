# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging
import threading
import typing

from odoo.modules import registry
from odoo.tools.lru import LRU
from odoo.tools.misc import OrderedSet

from .exceptions import (
    CacheInvalidConfigError,
    CacheInvalidDependencyError,
    CacheInvalidNameError,
)

__all__ = ("add_custom_cache",)

_logger = logging.getLogger(__name__)
_rlock = threading.RLock()


def add_custom_cache(
    name: str,
    count: int,
    depends_on_caches: typing.Iterable[str] = None,
    allows_direct_invalidation: bool = True,
    ignore_exceptions: typing.Iterable[type] = (),
):
    """Adds a custom cache into the Odoo registry

    :param name: name of the custom cache to add
    :param count: max capability of the custom cache; set as 1 if a lower value is
        given
    :param allows_direct_invalidation: if ``True``, a DB sequence is assigned to the
        cache is assigned any sequence and (therefore dotted names for such caches
        are not allowed) and method ``Registry.clear_cache()`` can be called
        directly for it
    :param depends_on_caches: iterable of other cache names: if set, the current
        cache will be listed as dependent on those caches, and invalidating one of
        them will invalidate the custom cache as well
    :param ignore_exceptions: iterable of Exception types: if set, no error is
        raised, but the cache is not added to the registries anyway
    """
    with _rlock:
        # Backup ``registry`` module attributes to restore if something goes wrong
        _registry_caches_backup = dict(registry._REGISTRY_CACHES)
        _caches_by_key_backup = dict(registry._CACHES_BY_KEY)

        # Try adding the cache to registry
        try:
            _add_custom_cache_try(
                name,
                count,
                depends_on_caches,
                allows_direct_invalidation,
            )
        # Handle exception if needed
        except Exception as exc:
            # Restores ``registry`` module attributes since something went wrong
            registry._REGISTRY_CACHES = dict(_registry_caches_backup)
            registry._CACHES_BY_KEY = dict(_caches_by_key_backup)
            _add_custom_cache_except(name, exc, ignore_exceptions)


def _add_custom_cache_try(
    name: str,
    count: int,
    depends_on_caches: typing.Iterable[str],
    allows_direct_invalidation: bool,
):
    _logger.info(f"Adding cache '{name}' to registries...")

    # ``registry._REGISTRY_CACHES`` is used by ``registry.Registry.init()`` to
    # initialize registries' caches (attr ``__cache``)
    _registry_caches = registry._REGISTRY_CACHES
    # ``registry._CACHES_BY_KEY`` is used by a variety of ``registry.Registry``
    # methods to handle caches dependencies and DB signaling (main reason why a
    # cache that allows direct invalidation cannot have a dotted name)
    _caches_by_key = registry._CACHES_BY_KEY

    # Step 1: add the cache name to the ``registry._REGISTRY_CACHES``, so new
    # registries will automatically use it upon initialization
    if name in _registry_caches:
        _logger.warning(f"Cache '{name}' already exists, skipping...")
        return
    normalized_count = max(count, 1)
    _registry_caches[name] = normalized_count

    # Step 2: define invalidation mechanism, either direct (if cache allows direct
    # invalidation) or indirect (meaning the cache is cleared when one of its
    # dependencies gets cleared)
    if allows_direct_invalidation:
        if "." in name:
            raise CacheInvalidNameError(f"Invalid cache name '{name}'")
        _caches_by_key[name] = (name,)
    elif not depends_on_caches:
        raise CacheInvalidConfigError(
            f"Cache '{name}' should either allow direct invalidation"
            f" or depend on another cache for indirect invalidation"
        )

    # Step 3: setup invalidation dependencies recursively: if cache-3 depends on
    # cache-2, and cache-2 depends on cache-1, then invalidating cache-1 should
    # invalidate both cache-2 and cache-3
    # NB: use an ``OrderedSet`` to avoid duplicates while keeping the dependency
    # order, then convert to tuple for consistency w/ the standard
    # ``registry._CACHES_BY_KEY`` structure
    if depends_on_caches:
        for cache_name in depends_on_caches or []:
            if cache_name not in _caches_by_key:
                raise CacheInvalidDependencyError(
                    f"Cache '{name}' cannot depend on cache '{cache_name}':"
                    f" '{cache_name}' doesn't exist or doesn't allow direct"
                    f" invalidation"
                )
            if name not in (dep_names := OrderedSet(_caches_by_key[cache_name])):
                _caches_by_key[cache_name] = tuple(dep_names | {name})
        to_check = list(_caches_by_key)
        while to_check:
            cache_name = to_check.pop(0)
            dep_names = OrderedSet([cache_name]) | _caches_by_key[cache_name]
            for dep_name in tuple(dep_names):
                for subdep_name in _caches_by_key.get(dep_name) or []:
                    if subdep_name not in dep_names:
                        dep_names.add(subdep_name)
                        if cache_name not in to_check:
                            to_check.append(cache_name)
            _caches_by_key[cache_name] = tuple(dep_names)

    # Step 4: update existing registries by:
    #   - adding the custom cache to the registry (with name-mangling to avoid
    #   ``AttributeError``)
    #   - setting up the proper signaling workflow
    # NB: ``registry.Registry.registries`` is a class attribute that returns an
    # ``odoo.tools.lru.LRU`` object that maps DB names to ``registry.Registry``
    # objects through its attribute ``d`` (an ``collections.OrderedDict`` object)
    for db_name, db_registry in registry.Registry.registries.d.items():
        _logger.info(f"Adding cache '{name}' to '{db_name}' registry")
        db_registry._Registry__caches[name] = LRU(normalized_count)
        if allows_direct_invalidation:
            db_registry.setup_signaling()


def _add_custom_cache_except(name, exc, ignore_exceptions):
    _logger.error(f"Could not add custom cache '{name}': {exc}")
    # Raise error unless specified otherwise
    ignore_exceptions = tuple(ignore_exceptions or ())
    if ignore_exceptions and isinstance(exc, ignore_exceptions):
        _logger.warning(
            f"While trying to add cache '{name}' to the registry,"
            f" an error occurred:\n{repr(exc) or str(exc)}"
        )
    else:
        raise
