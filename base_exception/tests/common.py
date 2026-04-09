# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

try:
    from decorator import decoratorx as decorator
except ImportError:
    from decorator import decorator

from contextlib import contextmanager
from unittest.mock import patch

from ..exceptions import BaseExceptionError


@decorator
def swallow_base_exception_error(func, self):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseExceptionError:
            return None

    return wrapper


@contextmanager
def mock_base_exception_method_env(self, env=None):
    if env is None:
        env = self.env
    with patch(
        "odoo.addons.base_exception.models.base_exception_method.Environment"
    ) as mocked_env:
        mocked_env.return_value = env
        yield


@decorator
def patch_base_exception_method_env(func, self):
    with mock_base_exception_method_env(self):
        return func(self)
