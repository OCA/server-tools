
import logging

from odoo.http import WebRequest
from odoo.sql_db import Cursor
from odoo import api

from .models.profiler_profile import ProfilerProfile

_logger = logging.getLogger(__name__)


def patch_web_request_call_function():
    """Modify Odoo entry points so that profile can record.

    Odoo is a multi-threaded program. Therefore, the :data:`profile` object
    needs to be enabled/disabled each in each thread to capture all the
    execution.

    For instance, Odoo spawns a new thread for each request.
    """
    _logger.info('Patching http.WebRequest._call_function')
    webreq_f_origin = WebRequest._call_function

    def webreq_f(*args, **kwargs):
        with ProfilerProfile.profiling():
            return webreq_f_origin(*args, **kwargs)
    WebRequest._call_function = webreq_f


def patch_call_kw_function():
    _logger.info('Patching odoo.api.call_kw')
    call_kw_f_origin = api.call_kw

    def call_kw_f(*args, **kwargs):
        with ProfilerProfile.profiling():
            return call_kw_f_origin(*args, **kwargs)
    api.call_kw = call_kw_f


def patch_cursor_init():
    _logger.info('Patching sql_dp.Cursor.__init__')
    cursor_f_origin = Cursor.__init__

    def init_f(self, *args, **kwargs):
        cursor_f_origin(self, *args, **kwargs)
        enable = ProfilerProfile.activate_deactivate_pglogs
        if enable is not None:
            self._obj.execute('SET log_min_duration_statement TO "%s"' %
                              ((not enable) * -1,))
    Cursor.__init__ = init_f


def post_load():
    patch_web_request_call_function()
    patch_call_kw_function()
    patch_cursor_init()
