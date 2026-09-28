import importlib

from odoo import http
from odoo.tests.common import TransactionCase
from odoo.tools import config

from odoo.addons.http_routing.tests.common import MockRequest

from .. import override


class TestDbfilterFromHeader(TransactionCase):
    def setUp(self):
        super().setUp()
        self.config_org = {}
        for key in ("proxy_mode", "server_wide_modules", "dbfilter", "db_name"):
            self.config_org[key] = config[key]
        self.db_filter_org = http.db_filter
        config["dbfilter"] = "^db1|db2$"
        config["proxy_mode"] = True
        config["server_wide_modules"] = "dbfilter_from_header"
        importlib.reload(override)

    def test_dbfilter_with_header(self):
        """
        Test that with a dbfilter set in config, it restricts what is selectable
        via the header
        """
        with MockRequest(self.env) as mock_request:
            mock_request.httprequest.environ["HTTP_X_ODOO_DBFILTER"] = "^db2|db3$"
            filtered_dbs = http.db_filter(["db1", "db2", "db3"])
        self.assertEqual(filtered_dbs, ["db2"])

    def test_dbfilter_without_header(self):
        """
        Test that with a dbfilter set in config and no header added, standard behavior
        is applied
        """
        with MockRequest(self.env):
            filtered_dbs = http.db_filter(["db1", "db2", "db3"])
        self.assertEqual(filtered_dbs, ["db1", "db2"])

    def test_no_dbfilter_with_header(self):
        """
        Test that with no dbfilter set in config, filter from header is unrestricted
        """
        config["dbfilter"] = ""
        config["db_name"] = ""
        with MockRequest(self.env) as mock_request:
            mock_request.httprequest.environ["HTTP_X_ODOO_DBFILTER"] = "^db2|db3$"
            filtered_dbs = http.db_filter(["db1", "db2", "db3"])
        self.assertEqual(filtered_dbs, ["db2", "db3"])

    def test_dbfilter_without_http_request(self):
        """
        Test that without an active HTTP request context (http.request is None),
        db_filter applies standard filtering without raising AttributeError.
        """
        http.request = None
        filtered_dbs = http.db_filter(["db1", "db2", "db3"])
        self.assertEqual(filtered_dbs, ["db1", "db2"])

    def test_dbfilter_without_httprequest(self):
        """
        Test that when http.request has no httprequest attribute,
        db_filter applies standard filtering without raising AttributeError.
        """

        class DummyRequest:
            httprequest = None

        http.request = DummyRequest()
        try:
            filtered_dbs = http.db_filter(["db1", "db2", "db3"])
            self.assertEqual(filtered_dbs, ["db1", "db2"])
        finally:
            http.request = None

    def test_dbfilter_with_invalid_regex_header(self):
        """
        Test that an invalid regex pattern in HTTP_X_ODOO_DBFILTER logs a warning
        and falls back gracefully without raising re.error.
        """
        with MockRequest(self.env) as mock_request:
            mock_request.httprequest.environ["HTTP_X_ODOO_DBFILTER"] = "[invalid(regex"
            with self.assertLogs(override._logger, level="WARNING") as cm:
                filtered_dbs = http.db_filter(["db1", "db2", "db3"])
            self.assertEqual(filtered_dbs, ["db1", "db2"])
            self.assertTrue(
                any(
                    "Invalid regex in X-Odoo-DBFilter header" in msg
                    for msg in cm.output
                )
            )

    def tearDown(self):
        super().tearDown()
        for key, value in self.config_org.items():
            config[key] = value
        http.db_filter = self.db_filter_org
