import importlib

from odoo import http
from odoo.tests.common import TransactionCase
from odoo.tools import config

from odoo.addons.website.tools import MockRequest

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

    def tearDown(self):
        super().tearDown()
        for key, value in self.config_org.items():
            config[key] = value
        http.db_filter = self.db_filter_org
