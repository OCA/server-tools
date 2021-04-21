# © 2021  CodingDodo (https://codingdodo.com)
# @author L ATTENTION Philippe <contact@codingdodo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo
from odoo.tests import common
from odoo.addons.dbfilter_from_header.override import db_filter
import inspect
from unittest.mock import Mock, patch


class TestDbfilterFromHeader(common.BaseCase):
    @patch.dict(
        "odoo.tools.config.options",
        {"proxy_mode": True, "dbfilter": False, "db_name": False},
    )
    def test_db_filter_override(self):
        def list_dbs(force=False):
            if not odoo.tools.config["list_db"] and not force:
                raise odoo.exceptions.AccessDenied()
            if not odoo.tools.config["dbfilter"] and odoo.tools.config["db_name"]:
                res = sorted(
                    db.strip() for db in odoo.tools.config["db_name"].split(",")
                )
                return res
            return ["oca_data_staging", "oca_data_production", "oca_test"]

        with patch.object(odoo.service.db, "list_dbs", list_dbs):
            httprequest = Mock(
                host="localhost",
                path="/",
                app=odoo.http.root,
                environ={
                    "REMOTE_ADDR": "127.0.0.1",
                    "HTTP_X_ODOO_DBFILTER": "oca_data_production",
                },
                cookies={},
                referrer="",
            )
            self.assertEqual(
                ["oca_data_staging", "oca_data_production", "oca_test"],
                odoo.service.db.list_dbs(True),
            )
            filtered_dbs = odoo.addons.dbfilter_from_header.override.db_filter(
                odoo.service.db.list_dbs(True), httprequest=httprequest
            )
            self.assertEqual(["oca_data_production"], filtered_dbs)

    @patch.dict(
        "odoo.tools.config.options",
        {
            "proxy_mode": True,
            "dbfilter": False,
            "server_wide_modules": ["web", "dbfilter_from_header"],
            "db_name": False,
        },
    )
    def test_class_http_is_monkey_patched(self):
        from odoo.addons.dbfilter_from_header import hooks

        hooks.post_load()
        self.assertEqual(odoo.tools.config.get("proxy_mode"), True)
        self.assertIn(
            "dbfilter_from_header", odoo.tools.config.get("server_wide_modules")
        )
        self.assertEqual(
            inspect.getsource(odoo.http.db_filter),
            inspect.getsource(odoo.addons.dbfilter_from_header.override.db_filter),
        )
