# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FakeProductFactory(models.Model):
    _name = "fake.product.factory"
    _description = "fake model for tests"

    name = fields.Char()
    code_mask = fields.Char()


class FakeProduct(models.Model):
    _name = "fake.product"
    _inherit = "code.format.mixin"
    _description = "fake model for tests"
    _code_mask = {"mask": "code_mask", "template": "tmpl_id"}
    tmpl_id = fields.Many2one("fake.product.factory")
    code = fields.Char()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.code = res._generate_code()
        return res
