# Copyright 2023 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import os
import threading
import time

from odoo.http import HttpRequest, JsonRequest
from odoo.tools import config as odoo_config

_logger = logging.getLogger(__name__)


def patch_dispatch_method(
    class_to_patch, min_duration_second: float = 30, level: str = "INFO"
):
    """Patch dispatch method to log slow calls

    :param class_to_patch: class to patch the dispatch method
    :param min_duration_second float: dispatch call running at least this
            number of seconds will be logged
    :param level str: logging level to use for logging
    """

    origin_dispatch_method = class_to_patch.dispatch

    def new_dispatch(self, *args, **kwargs):
        time0 = time.perf_counter()
        res = origin_dispatch_method(self, *args, **kwargs)
        computed_time = time.perf_counter() - time0
        if computed_time > min_duration_second:
            thread = threading.current_thread()
            _logger.log(
                logging._checkLevel(level),
                "Slow WSGI request processed in %.3fs: %r",
                computed_time,
                {
                    "RequestType": type(self),
                    "dbname": self.db,
                    "url": self.httprequest.url,
                    "uid": self.uid,
                    "params": self.params,
                    "context": self.context,
                    "total_time": computed_time,
                    "query_time": thread.query_time,
                    "python_time": computed_time - thread.query_time,
                    "query_count": thread.query_count,
                },
            )
        return res

    class_to_patch.dispatch = new_dispatch


def initialize_slow_wgsi_request_logger(config):
    _logger.info("Mocking WSGI Requests objects to log slow wsgi requests.")
    min_duration = float(
        os.environ.get(
            "ODOO_LOG_WSGI_REQUEST_MIN_DURATION",
            config.get("log_wsgi_request_min_duration", 30.0),
        )
    )
    level = os.environ.get(
        "ODOO_LOG_WSGI_REQUEST_LEVEL", config.get("log_wsgi_request_level", "DEBUG")
    )
    patch_dispatch_method(
        HttpRequest,
        min_duration_second=min_duration,
        level=level,
    )
    patch_dispatch_method(
        JsonRequest,
        min_duration_second=min_duration,
        level=level,
    )


def post_load():
    initialize_slow_wgsi_request_logger(odoo_config)
