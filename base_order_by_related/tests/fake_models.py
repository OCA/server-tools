# Copyright (C) 2023 Therp (<http://www.therp.nl>).
# @author Tom Blauwendraat <tblauwendraat@therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FakeCustomer(models.Model):
    _name = "fake.customer"
    _description = "fake model for customers"

    _order_by_related = ["country_name", "country_code", "fake_sortkey3"]

    name = fields.Char(required=True)
    sortkey1 = fields.Integer()
    sortkey2 = fields.Integer()
    sortkey3 = fields.Integer()
    country_id = fields.Many2one("res.country")
    country_name = fields.Char(related="country_id.name")
    country_code = fields.Char(related="country_id.code")
    fake_sortkey3 = fields.Integer(related="sortkey3")
