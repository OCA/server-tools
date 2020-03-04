# Copyright 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CleanupPurgeLineAction(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.action'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.action', 'Purge Wizard', readonly=True)
    action_id = fields.Many2one('ir.actions.act_window', 'Action entry')
    action_model = fields.Char(related="action_id.res_model", string="Missing model")
    action_external_id = fields.Char(
        size=128,
        string="External ID",
        help="ID of the window action defined in xml file"
    )

    @api.multi
    def purge(self):
        """Unlink action entries upon manual confirmation."""
        if self:
            objs = self
        else:
            objs = self.env['cleanup.purge.line.action']\
                .browse(self._context.get('active_ids'))
        to_unlink = objs.filtered(lambda x: not x.purged and x.action_id)
        self.logger.info('Purging window action entries: %s', to_unlink.mapped('name'))
        to_unlink.mapped('action_id').unlink()
        return to_unlink.write({'purged': True})


class CleanupPurgeWizardAction(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.action'
    _description = 'Purge window actions'

    @api.model
    def find(self):
        """
        Search for models that cannot be instantiated.
        """
        res = []
        for action in self.env['ir.actions.act_window'].with_context(active_test=False)\
                .search([('res_model', '!=', False)]):

            if (action.res_model not in self.env):
                res.append((0, 0, {
                    'name': action.name,
                    'action_id': action.id,
                    'action_external_id': action.get_external_id(),
                }))
        if not res:
            raise UserError(_('No dangling window action entries found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.action', 'wizard_id', 'Window actions to purge')
