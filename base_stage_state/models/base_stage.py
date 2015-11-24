# -*- coding: utf-8 -*-
# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class BaseStageSet(models.Model):
    """
    Organize Stages in Sets
    """
    _name = 'base.stage.set'
    _description = 'Base Stage Set'
    name = fields.Char(translate=True)
    stage_ids = fields.One2many('base.stage', 'stage_set_id', 'Stages')


class BaseStage(models.Model):
    _name = 'base.stage'
    _description = 'Generic Stage'
    _order = 'stage_set_id, sequence'

    @api.model
    def _get_states(self):
        return [
            ('draft', 'New'),
            ('open', 'In Progress'),
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled')]

    @api.model
    def get_default_stage(self, model):
        domain = [('model_id', '=', model), ('fold', '=', False)]
        return self.search(domain, limit=1)

    stage_set_id = fields.Many2one(
        'base.stage.set', 'Stage Set', required=True)
    sequence = fields.Integer('Sequence', default=1, index=True)
    name = fields.Char('Stage Name', required=True, translate=True)
    description = fields.Text('Description')
    case_default = fields.Boolean(
        'Default for New Projects',
        help="When checked, this stage will be proposed by default.")
    fold = fields.Boolean(
        'Folded in Kanban View',
        help='This stage is folded in the kanban view when'
             'there are no records in that stage to display.')
    state = fields.Selection(
        _get_states, string="State",
        help="Common canonical stages easier to use "
             "in custom business logic.")
