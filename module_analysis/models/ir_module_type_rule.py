# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class IrModuleType(models.Model):
    _name = "ir.module.type.rule"
    _description = "Modules Types Rules"
    _order = "sequence"

    sequence = fields.Integer(string="Sequence")

    module_domain = fields.Char(string="Module Domain", required=True, default="[]")

    module_type_id = fields.Many2one(
        string="Module type", comodel_name="ir.module.type", required=True
    )

    def _get_module_type_id_from_module(self, module):
        IrModuleModule = self.env["ir.module.module"]
        for rule in self:
            domain = safe_eval(rule.module_domain)
            domain.append(("id", "=", module.id))
            if IrModuleModule.search(domain):
                return rule.module_type_id.id
        return False
