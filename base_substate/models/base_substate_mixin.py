# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class BaseSubstateMixin(models.AbstractModel):
    _name = "baase.substate.mixin"
    _description = 'BaseSubstate Mixin'

    substate_id = fields.Many2one('base.state', string='Sub State', ondelete='restrict',
        default='_get_default_substate_id',
        domain="[('model', '=', self._name)]", copy=False)

    def _get_default_substate_id(self):
        """ Gives default substate_id """
        if not project_id:
            return False
        search_domain =  self._get_default_substate_domain()
        # perform search, return the first found
        return self.env['base.substate'].search(search_domain, order='sequence', limit=1).id 

    def _get_default_substate_domain(self):
        """ Override this method
            to change domain values
        """
        state_val = self._get_default_state_value()
        substate_type = self._get_substate_type()
        state_field =  substate_type.target_state_field
        if self and state_field in self._fields:
            state_val = self[state_field]

        domain += (('target_state_value.target_state_value', '=', state_val))
        domain += (('target_state_value.base_substate_type', '=', substate_type.id))
        return domain

    def _get_default_state_value(self,):
        """ Override this method
            to change state_value
            """
        return 'draft'
 
    def _get_substate_type(self,):
        """ Override this method
            to change substate_type (get by xml id for example)
        """
        return self.env['base.substate.type'].search([('model', '=', self._name)], limit=1)

