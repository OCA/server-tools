# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    def _prepare_update(self):
        """this function crashes for undefined models"""
        self = self.filtered(lambda x: x.model in self.env)
        return super()._prepare_update()
