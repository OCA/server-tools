# Copyright 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CleanupPurgeLineView(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.view'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.view', 'Purge Wizard', readonly=True)
    view_id = fields.Many2one('ir.ui.view', 'View entry')
    view_model = fields.Char(related="view_id.model", string="Missing model")
    view_external_id = fields.Char(
        size=128,
        string="External ID",
        help="ID of the view defined in xml file"
    )

    @api.multi
    def purge(self):
        """Unlink view entries upon manual confirmation."""
        if self:
            objs = self
        else:
            objs = self.env['cleanup.purge.line.view']\
                .browse(self._context.get('active_ids'))
        to_unlink = objs.filtered(lambda x: not x.purged and x.view_id)
        self.logger.info('Purging view entries: %s', to_unlink.mapped('name'))
        to_unlink.mapped('view_id').unlink()
        return to_unlink.write({'purged': True})


class CleanupPurgeWizardView(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.view'
    _description = 'Purge views'

    @api.model
    def find(self):
        """
        Search for views that cannot be displayed.
        """
        res = []
        for view in self.env['ir.ui.view'].with_context(active_test=False)\
                .search([('model', '!=', False)]):

            if (view.model and view.model not in self.env):
                res.append((0, 0, {
                    'name': view.name,
                    'view_id': view.id,
                    'view_external_id': view.get_external_id(),
                }))
        if not res:
            raise UserError(_('No dangling view entries found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.view', 'wizard_id', 'views to purge')
