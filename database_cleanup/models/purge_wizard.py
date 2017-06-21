# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import _, api, fields, models
from odoo.exceptions import AccessDenied


class CleanupPurgeLine(models.AbstractModel):
    """ Abstract base class for the purge wizard lines """
    _name = 'cleanup.purge.line'
    _order = 'name'

    name = fields.Char('Name', readonly=True)
    purged = fields.Boolean('Purged', readonly=True)
    wizard_id = fields.Many2one('cleanup.purge.wizard')

    logger = logging.getLogger('odoo.addons.database_cleanup')

    @api.multi
    def purge(self):
        raise NotImplementedError

    @api.model
    def create(self, values):
        # make sure the user trying this is actually supposed to do it
        if self.env.ref(
                'base.group_erp_manager') not in self.env.user.groups_id:
            raise AccessDenied
        return super(CleanupPurgeLine, self).create(values)


class PurgeWizard(models.AbstractModel):
    """ Abstract base class for the purge wizards """
    _name = 'cleanup.purge.wizard'
    _description = 'Purge stuff'

    @api.model
    def default_get(self, fields_list):
        res = super(PurgeWizard, self).default_get(fields_list)
        if 'purge_line_ids' in fields_list:
            res['purge_line_ids'] = self.find()
        return res

    @api.multi
    def find(self):
        raise NotImplementedError

    @api.multi
    def purge_all(self):
        self.mapped('purge_line_ids').purge()
        return True

    @api.model
    def get_wizard_action(self):
        wizard = self.create({})
        return {
            'type': 'ir.actions.act_window',
            'name': wizard.display_name,
            'views': [(False, 'form')],
            'res_model': self._name,
            'res_id': wizard.id,
            'flags': {
                'action_buttons': False,
                'sidebar': False,
            },
        }

    @api.multi
    def select_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Select lines to purge'),
            'views': [(False, 'tree'), (False, 'form')],
            'res_model': self._fields['purge_line_ids'].comodel_name,
            'domain': [('wizard_id', 'in', self.ids)],
        }

    @api.multi
    def name_get(self):
        return [
            (this.id, self._description)
            for this in self
        ]

    @api.model
    def create(self, values):
        # make sure the user trying this is actually supposed to do it
        if self.env.ref(
                'base.group_erp_manager') not in self.env.user.groups_id:
            raise AccessDenied
        return super(PurgeWizard, self).create(values)

    purge_line_ids = fields.One2many('cleanup.purge.line', 'wizard_id')
