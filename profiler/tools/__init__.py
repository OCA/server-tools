# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from .decorator import profiled
from . import dynamic_profile

__all__ = ["profiled", "dynamic_profile"]
