# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from contextlib import contextmanager
from contextvars import ContextVar

from odoo.api import Environment, Environments
from odoo.tools import classproperty

_logger = logging.getLogger(__name__)

_odoo_environments_ctx = ContextVar("odoo.environments", default=())


@classproperty
def contextvars_envs(_cls):
    envs = _odoo_environments_ctx.get()
    if not envs:
        # Look in _local in case we use this while the non patched context manager
        # is active
        envs = getattr(_cls._local, "environments", ())
        if envs:
            # is case that an envs exist set it to context manager
            # This can occure with pytest
            _odoo_environments_ctx.set(envs)
    return envs


@classmethod  # type: ignore
@contextmanager
def contextvars_manage(_cls):
    """Context manager for a set of environments."""
    if _odoo_environments_ctx.get():
        yield
    else:
        try:
            # First look in _local in case we use this patched context manager
            # while the non patched one is active.
            _odoo_environments_ctx.set(
                getattr(_cls._local, "environments", ()) or Environments()
            )
            _logger.debug("envs manage start")
            yield
        finally:
            _logger.debug("envs manage end")
            _odoo_environments_ctx.set(())


@classmethod  # type: ignore
def contextvars_reset(_cls):
    """Clear the set of environments.
    This may be useful when recreating a registry inside a transaction.
    """
    envs = Environments()
    if getattr(_cls._local, "environments", ()):
        # In case the non patched context manager is active.
        _cls._local.environments = envs
    _odoo_environments_ctx.set(envs)


Environment.envs = contextvars_envs

Environment.manage = contextvars_manage

Environment.reset = contextvars_reset

_logger.info("Patched odoo.api.Environment to use contextvars")
