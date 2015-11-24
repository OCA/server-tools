# -*- coding: utf-8 -*-
# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, fields, api


class BaseStageMixin(models.AbstractModel):
    _name = "base.stage.mixin"
    _description = "Stage Aware Model"

    @api.model
    def _get_default_stage(self):
        """ Gives default stage_id """
        return self.env['base.stages'].get_default_stage(self._name)

    stage_id = fields.Many2one(
        'base.stage', 'Stage',
        track_visibility='always', index=True,
        domain="[('model_name', '=', self._name)]",
        default=_get_default_stage,
        copy=False)
    state = fields.Selection(
        related='stage_id.state', readonly=True, store=True)

    # Kanban fields
    kanban_state = fields.Selection(
        [('normal', 'Normal'),
         ('blocked', 'Blocked'),
         ('done', 'Ready for next stage')],
        'Kanban State',
        track_visibility='onchange',
        default='normal',
        copy=False,
        help="The kanban state indicates the workflow readiness:\n"
             " * Normal is the default situation\n"
             " * Blocked indicates something is preventing progress\n"
             " * Ready for next stage indicates it is ready"
             " to be pulled to the next stage")
    color = fields.Integer('Color Index')

    @api.multi
    def _read_group_stage_ids(self, domain,
                              read_group_order=None, access_rights_uid=None):
        stage_sets = self.mapped('stage_id.stage_set_id')
        domain = [('stage_set_id', 'in', stage_sets)]
        stages = self.stage_ids._search(
            domain, access_rights_uid=access_rights_uid)
        result = [(x.id, x.display_name) for x in stages]
        fold = {x.id: x.fold for x in stages}
        return result, fold

    _group_by_full = {
        'stage_id': _read_group_stage_ids,
    }
