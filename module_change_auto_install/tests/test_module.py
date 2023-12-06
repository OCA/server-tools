# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.module_change_auto_install.patch import (
    _get_modules_dict_auto_install_config,
)

# from ..models.base import disable_changeset


class TestModule(TransactionCase):
    _EXPECTED_RESULTS = {
        "web_responsive": {"web_responsive": True},
        "sale, purchase,": {"sale": True, "purchase": True},
        "web_responsive:web,base_technical_features:,"
        "point_of_sale:sale/purchase,account_usability": {
            "web_responsive": ["web"],
            "base_technical_features": [],
            "point_of_sale": ["sale", "purchase"],
            "account_usability": True,
        },
    }

    def test_config_parsing(self):
        for k, v in self._EXPECTED_RESULTS.items():
            self.assertEqual(_get_modules_dict_auto_install_config(k), v)
