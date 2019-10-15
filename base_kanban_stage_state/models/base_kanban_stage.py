# Copyright 2017 Specialty Medical Drugstore
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class BaseKanbanStage(models.Model):
    _inherit = 'base.kanban.stage'

    @api.model
    def _get_states(self):
        return [('draft', 'New'),
                ('open', 'In Progress'),
                ('pending', 'Pending'),
                ('done', 'Done'),
                ('cancelled', 'Cancelled'),
                ('exception', 'Exception')]

    state = fields.Selection(_get_states, string='State')
