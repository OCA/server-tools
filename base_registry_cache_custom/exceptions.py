# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


class CacheError(Exception):
    """Base error for invalid cache configuration"""


class CacheInvalidConfigError(CacheError):
    """Invalid cache configuration"""


class CacheInvalidDependencyError(CacheInvalidConfigError):
    """Invalid cache dependency"""


class CacheInvalidNameError(CacheInvalidConfigError):
    """Invalid cache name"""
