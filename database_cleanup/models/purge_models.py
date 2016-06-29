# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, models, fields
from openerp.exceptions import UserError
from openerp.addons.base.ir.ir_model import MODULE_UNINSTALL_FLAG


class IrModel(models.Model):
    _inherit = 'ir.model'

    @api.multi
    def _drop_table(self):
        # Allow to skip this step during model unlink
        # The super method crashes if the model cannot be instantiated
        if self.env.context.get('no_drop_table'):
            return True
        return super(IrModel, self)._drop_table()

    @api.multi
    def _inherited_models(self, field_name, arg):
        """this function crashes for undefined models"""
        result = dict((i, []) for i in self.ids)
        existing_model_ids = [
            this.id for this in self if this.model in self.env
        ]
        super_result = super(IrModel, self.browse(existing_model_ids))\
            ._inherited_models(field_name, arg)
        result.update(super_result)
        return result

    def _register_hook(self, cr):
        # patch the function field instead of overwriting it
        if self._columns['inherited_model_ids']._fnct !=\
                self._inherited_models.__func__:
            self._columns['inherited_model_ids']._fnct =\
                self._inherited_models.__func__
        return super(IrModel, self)._register_hook(cr)


class CleanupPurgeLineModel(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.model'
    _description = 'Purge models'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.model', 'Purge Wizard', readonly=True)

    @api.multi
    def purge(self):
        """
        Unlink models upon manual confirmation.
        """
        context_flags = {
            MODULE_UNINSTALL_FLAG: True,
            'no_drop_table': True,
        }

        for line in self:
            self.env.cr.execute(
                "SELECT id, model from ir_model WHERE model = %s",
                (line.name,))
            row = self.env.cr.fetchone()
            if not row:
                continue
            self.logger.info('Purging model %s', row[1])
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', line.name)
            ])
            if attachments:
                self.env.cr.execute(
                    "UPDATE ir_attachment SET res_model = NULL "
                    "WHERE id in %s",
                    (tuple(attachments.ids), ))
            self.env['ir.model.constraint'].search([
                ('model', '=', line.name),
            ]).unlink()
            relations = self.env['ir.model.fields'].search([
                ('relation', '=', row[1]),
            ]).with_context(**context_flags)
            for relation in relations:
                try:
                    # Fails if the model on the target side
                    # cannot be instantiated
                    relation.unlink()
                except KeyError:
                    pass
                except AttributeError:
                    pass
            self.env['ir.model.relation'].search([
                ('model', '=', line.name)
            ]).with_context(**context_flags).unlink()
            self.env['ir.model'].browse([row[0]])\
                .with_context(**context_flags).unlink()
            line.write({'purged': True})
        return True


class CleanupPurgeWizardModel(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.model'
    _description = 'Purge models'

    @api.model
    def find(self):
        """
        Search for models that cannot be instantiated.
        """
        res = []
        self.env.cr.execute("SELECT model from ir_model")
        for model, in self.env.cr.fetchall():
            if model not in self.env:
                res.append((0, 0, {'name': model}))
        if not res:
            raise UserError(_('No orphaned models found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.model', 'wizard_id', 'Models to purge')
