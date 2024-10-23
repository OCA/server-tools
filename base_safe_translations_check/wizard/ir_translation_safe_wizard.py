# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrTranslationSafeWizard(models.TransientModel):

    _name = "ir.translation.safe.wizard"
    _description = "Wizard to check existing translations."

    @api.model
    def _compute_module_selection(self):
        modules = self.env["ir.module.module"].search([])
        return modules.mapped(lambda m: (m.name, m.shortdesc))

    module = fields.Selection(selection=_compute_module_selection)
    lang_id = fields.Many2one(
        string="lang",
        comodel_name="res.lang",
        help="If set, only checks translation in that language",
    )

    def execute(self):
        self._execute()

    def _execute(self):
        self.ensure_one()
        domain = [("value", "not in", [False, ""])]
        if self.module:
            domain.append(("module", "=", self.module))
        if self.lang_id:
            domain.append(("lang", "=", self.lang_id.code))
        translations = self.env["ir.translation"].search(domain)
        # for translation in translations:
        translations.with_delay().jobify_check_constraints()
        return translations
