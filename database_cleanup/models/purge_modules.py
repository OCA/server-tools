# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.modules.registry import RegistryManager
from odoo.modules.module import get_module_path
from odoo.addons.base.ir.ir_model import MODULE_UNINSTALL_FLAG


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    @api.model
    def _module_data_uninstall(self, modules_to_remove):
        """this function crashes for xmlids on undefined models or fields
        referring to undefined models"""
        for this in self.search([('module', 'in', modules_to_remove)]):
            if this.model == 'ir.model.fields':
                field = self.env[this.model].with_context(
                    **{MODULE_UNINSTALL_FLAG: True}).browse(this.res_id)
                if not field.exists() or field.model not in self.env:
                    this.unlink()
                    continue
            if this.model not in self.env:
                this.unlink()
        return super(IrModelData, self)._module_data_uninstall(
            modules_to_remove)


class CleanupPurgeLineModule(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.module'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.module', 'Purge Wizard', readonly=True)

    @api.multi
    def purge(self):
        """
        Uninstall modules upon manual confirmation, then reload
        the database.
        """
        if self:
            objs = self
        else:
            objs = self.env['cleanup.purge.line.module']\
                .browse(self._context.get('active_ids'))
        module_names = objs.filtered(lambda x: not x.purged).mapped('name')
        modules = self.env['ir.module.module'].search([
            ('name', 'in', module_names)
        ])
        if not modules:
            return True
        self.logger.info('Purging modules %s', ', '.join(module_names))
        modules.button_uninstall()
        # we need this commit because reloading the registry would roll back
        # our changes
        self.env.cr.commit()  # pylint: disable=invalid-commit
        RegistryManager.new(self.env.cr.dbname, update_module=True)
        modules.unlink()
        return objs.write({'purged': True})


class CleanupPurgeWizardModule(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.module'
    _description = 'Purge modules'

    @api.model
    def find(self):
        res = []
        for module in self.env['ir.module.module'].search([]):
            if get_module_path(module.name):
                continue
            if module.state == 'uninstalled':
                self.env['cleanup.purge.line.module'].create({
                    'name': module.name,
                }).purge()
                continue
            res.append((0, 0, {'name': module.name}))

        if not res:
            raise UserError(_('No modules found to purge'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.module', 'wizard_id', 'Modules to purge')
