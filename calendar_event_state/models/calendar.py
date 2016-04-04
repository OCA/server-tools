# -*- coding: utf-8 -*-
# Copyright 2016 Alessio Gerace - Agile Business Group
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, fields, api


class CalendarEventStates(models.Model):
    _name = 'calendar.event.state'
    _description = 'Calendar State'
    _order = 'sequence'

    @api.model
    def _default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(
        'res.company', 'company', default=_default_company)

    name = fields.Char('State Name', required=True, translate=True)

    sequence = fields.Integer('Sequence', default=1)

    event_ids = fields.One2many(
        'calendar.event', 'state_id',
        'Related Events')

    fold = fields.Boolean(
        'Folded in Kanban View',
        help='This state is folded in the kanban view.'
    )


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'
    _order = "priority desc"

    state_id = fields.Many2one(
        'calendar.event.state', 'State',
        select=True, copy=False)

    priority = fields.Selection(
        [('0', 'Low'),
         ('1', 'Normal'),
         ('2', 'High')],
        'Priority', select=True)

    note = fields.Text("Internal Notes")

    @api.model
    def _state_groups(self, present_ids, domain, **kwargs):
        states = self.env['calendar.event.state'].search(
            [
                ('company_id', '=', self.env.user.company_id.id)
            ])
        foldeds = {}
        for s in states:
            foldeds[s.id] = int(s.fold)
        data = [(s.id, s.name) for s in states]
        return data, foldeds

    _group_by_full = {
        'state_id': _state_groups,
    }
