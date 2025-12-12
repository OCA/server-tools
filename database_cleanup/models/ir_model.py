# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, models


class IrModel(models.Model):
    _inherit = "ir.model"

    def _drop_table(self):
        """this function crashes for undefined models"""
        self = self.filtered(lambda x: x.model in self.env)
        return super()._drop_table()

    @api.depends()
    def _inherited_models(self):
        """this function crashes for undefined models"""
        self = self.filtered(lambda x: x.model in self.env)
        return super()._inherited_models()
