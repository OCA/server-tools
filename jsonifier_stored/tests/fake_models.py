# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FakeTestModel(models.Model):

    _name = "json.stored.fake.model"
    _inherit = "jsonifier.stored.mixin"
    _description = _name

    name = fields.Char()
    description = fields.Text()

    def _jsonify_get_exporter(self):
        return self.env.ref("jsonifier_stored.ir_exp_test")


class FakeTestModelMultiLang(models.Model):

    _name = "json.stored.fake.model.multilang"
    _inherit = "jsonifier.stored.mixin"
    _description = _name

    name = fields.Char(translate=True)
    description = fields.Text()
    lang_id = fields.Many2one("res.lang")
    title_id = fields.Many2one("res.partner.title")

    def _jsonify_get_exporter(self):
        return self.env.ref("jsonifier_stored.ir_exp_test_multilang")
