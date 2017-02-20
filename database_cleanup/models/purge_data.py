# -*- coding: utf-8 -*-
# © 2014-2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError
from ..identifier_adapter import IdentifierAdapter


class CleanupPurgeLineData(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.data'

    data_id = fields.Many2one('ir.model.data', 'Data entry')
    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.data', 'Purge Wizard', readonly=True)

    @api.multi
    def purge(self):
        """Unlink data entries upon manual confirmation."""
        to_unlink = self.filtered(lambda x: not x.purged and x.data_id)
        self.logger.info('Purging data entries: %s', to_unlink.mapped('name'))
        to_unlink.mapped('data_id').unlink()
        return self.write({'purged': True})


class CleanupPurgeWizardData(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.data'
    _description = 'Purge data'

    @api.model
    def find(self):
        """Collect all rows from ir_model_data that refer
        to a nonexisting model, or to a nonexisting
        row in the model's table."""
        res = []
        data_ids = []
        unknown_models = []
        self.env.cr.execute("""SELECT DISTINCT(model) FROM ir_model_data""")
        for model, in self.env.cr.fetchall():
            if not model:
                continue
            if model not in self.env.registry:
                unknown_models.append(model)
                continue
            self.env.cr.execute(
                """
                SELECT id FROM ir_model_data
                WHERE model = %s
                AND res_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT id FROM %s WHERE id=ir_model_data.res_id)
                """, (model, IdentifierAdapter(self.env[model]._table)))
            data_ids.extend(data_row for data_row, in self.env.cr.fetchall())
        data_ids += self.env['ir.model.data'].search([
            ('model', 'in', unknown_models),
        ]).ids
        for data in self.env['ir.model.data'].browse(data_ids):
            res.append((0, 0, {
                        'data_id': data.id,
                        'name': "%s.%s, object of type %s" % (
                            data.module, data.name, data.model)}))
        if not res:
            raise UserError(_('No orphaned data entries found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.data', 'wizard_id', 'Data to purge')
