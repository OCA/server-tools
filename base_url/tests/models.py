# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FakeProduct(models.Model):
    _inherit = ["abstract.url"]
    _name = "fake.product"

    code = fields.Char()
    name = fields.Char(translate=True)
    active = fields.Boolean(default=True)
    categ_id = fields.Many2one("fake.categ")

    def _get_keyword_fields(self):
        return ["categ_id.name"] + super()._get_keyword_fields() + ["code"]


class FakeCateg(models.Model):
    _name = "fake.categ"

    name = fields.Char()
