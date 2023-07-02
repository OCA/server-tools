# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    test_field = fields.Char()
    test_field_2 = fields.Integer()

    def test_function(self):
        """Just a test function"""
        raise NotImplementedError()
