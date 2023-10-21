# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.modules.registry import Registry
from odoo.osv.expression import AND

from ..blacklist import (
    BLACKLIST_MODULES,
    BLACKLIST_MODULES_ENDS_WITH,
    BLACKLIST_MODULES_STARTS_WITH,
)


class UpgradeInstallWizard(models.TransientModel):
    _name = "upgrade.install.wizard"
    _description = "Upgrade Install Wizard"

    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")], readonly=True, default="draft"
    )

    module_ids = fields.Many2many(
        comodel_name="ir.module.module",
        domain=lambda x: x._module_ids_domain(),
    )

    module_qty = fields.Integer(
        string="Modules Quantity", compute="_compute_module_qty"
    )

    @api.model
    def _module_ids_domain(self, extra_domain=None):
        domain = [
            "&",
            ("state", "not in", ["installed", "uninstallable", "unknown"]),
            ("name", "not in", BLACKLIST_MODULES),
        ]
        if extra_domain:
            domain = AND([domain, extra_domain])
        modules = self.env["ir.module.module"].search(domain)

        for start_pattern in BLACKLIST_MODULES_STARTS_WITH:
            modules = modules.filtered(
                lambda x, start_pattern=start_pattern: not x.name.startswith(
                    start_pattern
                )
            )
        for end_pattern in BLACKLIST_MODULES_ENDS_WITH:
            modules = modules.filtered(
                lambda x, end_pattern=end_pattern: not x.name.endswith(end_pattern)
            )
        return [("id", "in", modules.ids)]

    @api.depends("module_ids")
    def _compute_module_qty(self):
        for wizard in self:
            wizard.module_qty = len(wizard.module_ids)

    def select_odoo_modules(self, extra_domain=None):
        self.ensure_one()
        modules = self.env["ir.module.module"].search(
            self._module_ids_domain(extra_domain=extra_domain)
        )
        modules = modules.filtered(lambda x: x.is_odoo_module)
        self.module_ids = modules
        return self.return_same_form_view()

    def select_oca_modules(self, extra_domain=None):
        self.ensure_one()
        modules = self.env["ir.module.module"].search(
            self._module_ids_domain(extra_domain=extra_domain)
        )
        modules = modules.filtered(lambda x: x.is_oca_module)
        self.module_ids = modules
        return self.return_same_form_view()

    def select_other_modules(self, extra_domain=None):
        self.ensure_one()
        modules = self.env["ir.module.module"].search(
            self._module_ids_domain(extra_domain=extra_domain)
        )
        modules = modules.filtered(lambda x: not (x.is_oca_module or x.is_odoo_module))
        self.module_ids = modules
        return self.return_same_form_view()

    def select_installable_modules(self, extra_domain=None):
        self.ensure_one()
        self.module_ids = self.env["ir.module.module"].search(
            self._module_ids_domain(extra_domain=extra_domain)
        )
        return self.return_same_form_view()

    def unselect_modules(self):
        self.ensure_one()
        self.module_ids = False
        return self.return_same_form_view()

    def install_modules(self):
        """Set all selected modules and actually install them."""
        self.ensure_one()
        self.module_ids.write({"state": "to install"})
        self.env.cr.commit()  # pylint: disable=invalid-commit
        Registry.new(self.env.cr.dbname, update_module=True)
        self.write({"state": "done"})
        return self.return_same_form_view()

    def return_same_form_view(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "upgrade.install.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }
