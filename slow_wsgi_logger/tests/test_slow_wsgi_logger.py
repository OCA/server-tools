import logging
from time import sleep

from odoo_test_helper import FakeModelLoader

import odoo.tools
from odoo import http
from odoo.tests import common, tagged
from odoo.tests.common import HttpCase, HttpSavepointCase

from odoo.addons.web.controllers.main import Home

from ..slow_wsgi_logger_middleware import initialize_slow_wgsi_request_logger

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestSlowWSGILoggerHttpRequest(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.min_duration = 0.1
        cls.level = "WARN"
        config = {}
        config["log_wsgi_request_min_duration"] = str(cls.min_duration)
        config["log_wsgi_request_level"] = cls.level

        from odoo.http import HttpRequest, JsonRequest

        previous_http_request_dispatch = HttpRequest.dispatch
        previous_json_request_dispatch = JsonRequest.dispatch

        # WebRequest class are already patch as initialize_slow_wgsi_request_logger
        # is called before launching test but with the configured or default
        # log_wsgi_request_min_duration which should not be a matter as long
        # it configure greater than cls.min_duration
        initialize_slow_wgsi_request_logger(config)

        def restore_dispatch():
            HttpRequest.dispatch = previous_http_request_dispatch
            JsonRequest.dispatch = previous_json_request_dispatch

        cls.addClassCleanup(restore_dispatch)

    def setUp(self):
        super().setUp()

        def waiting_route(self, wait="0.1"):
            wait = float(wait)
            sleep(wait)
            return "ok"

        waiting_route.routing_type = "http"
        self.env["ir.http"]._clear_routing_map()
        # patch Home to add test endpoint
        Home.waiting_route = http.route("/waiting", type="http", auth="none")(
            waiting_route
        )

        def _cleanup():
            # remove endpoint and destroy routing map
            del Home.waiting_route
            self.env["ir.http"]._clear_routing_map()

        self.addCleanup(_cleanup)

    def test_slow_http_should_logged(self):
        wait = self.min_duration + 0.1

        with self.assertLogs(
            "odoo.addons.slow_wsgi_logger.slow_wsgi_logger_middleware", level=self.level
        ) as cm:
            self.url_open(f"/waiting?wait={wait}", allow_redirects=False)
        self.assertEqual(len(cm.output), 1, cm.output)
        self.assertEqual(
            cm.records[0].levelno, logging._checkLevel(self.level), cm.output
        )
        self.assertTrue(
            cm.records[0].msg.startswith("Slow WSGI request processed in"), cm.output
        )

    def test_fast_http_should_not_logged(self):
        wait = self.min_duration - 0.1
        # assertNoLogs would be better here but present from python 3.10 and greater
        with self.assertLogs("odoo.addons.slow_wsgi_logger", level="DEBUG") as cm:
            self.url_open(f"/waiting?wait={wait}", allow_redirects=False)
            # log something in debug juste to avoid raising because nothing logged
            _logger.debug("the only expected log")
        self.assertEqual(len(cm.output), 1, cm.output)
        self.assertEqual(cm.records[0].levelno, logging.DEBUG)
        self.assertEqual(cm.records[0].msg, "the only expected log")


@tagged("post_install", "-at_install")
class TestSlowWSGILoggerJSONRPCRequest(HttpSavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.min_duration = 0.1
        cls.level = "WARN"
        config = {}
        config["log_wsgi_request_min_duration"] = str(cls.min_duration)
        config["log_wsgi_request_level"] = cls.level

        from odoo.http import HttpRequest, JsonRequest

        previous_http_request_dispatch = HttpRequest.dispatch
        previous_json_request_dispatch = JsonRequest.dispatch

        initialize_slow_wgsi_request_logger(config)

        def restore_dispatch():
            HttpRequest.dispatch = previous_http_request_dispatch
            JsonRequest.dispatch = previous_json_request_dispatch

        cls.addClassCleanup(restore_dispatch)

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.addClassCleanup(cls.loader.restore_registry)

        cls.loader.backup_registry()
        from .fake_test_model import FakeTestModel

        cls.loader.update_registry((FakeTestModel,))

    def setUp(self):
        super().setUp()
        self.admin_uid = self.env.ref("base.user_admin").id
        self.db_name = common.get_db_name()
        self.uid = self.xmlrpc_common.login(self.db_name, "admin", "admin")
        self.json_rpc_url = "http://%s:%s/jsonrpc" % (
            common.HOST,
            odoo.tools.config["http_port"],
        )

    def tearDown(self):
        super().tearDown()
        self.loader.restore_registry()

    def _json_call(self, *args, headers=None):
        return self.opener.post(
            self.json_rpc_url,
            json={
                "jsonrpc": "2.0",
                "id": None,
                "method": "call",
                "params": {"service": "object", "method": "execute", "args": args},
            },
            allow_redirects=False,
            headers=headers,
        )

    def test_slow_name_search_should_logged(self):
        wait = self.min_duration + 0.1
        with self.assertLogs("odoo.addons.slow_wsgi_logger", level=self.level) as cm:
            self._json_call(
                self.db_name,
                self.admin_uid,
                "admin",
                "fake.test",
                "name_search",
                wait,
            )

        self.assertEqual(len(cm.output), 1, cm.output)
        self.assertEqual(
            cm.records[0].levelno, logging._checkLevel(self.level), cm.output
        )
        self.assertTrue(
            cm.records[0].msg.startswith("Slow WSGI request processed in"), cm.output
        )

    def test_fast_http_should_not_logged(self):
        wait = self.min_duration - 0.1
        # assertNoLogs would be better here but present from python 3.10 and greater
        with self.assertLogs("odoo.addons.slow_wsgi_logger", level="DEBUG") as cm:
            self._json_call(
                self.db_name,
                self.admin_uid,
                "admin",
                "fake.test",
                "name_search",
                wait,
            )
            # log something in debug juste to avoid raising because nothing logged
            _logger.debug("the only expected log")
        self.assertEqual(len(cm.output), 1, cm.output)
        self.assertEqual(cm.records[0].levelno, logging.DEBUG)
        self.assertEqual(cm.records[0].msg, "the only expected log")
