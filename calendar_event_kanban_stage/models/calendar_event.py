# -*- coding: utf-8 -*-
# Copyright 2017 Alex Comba - Agile Business Group
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CalendarEvent(models.Model):
    _name = 'calendar.event'
    _inherit = ['calendar.event', 'base.kanban.abstract']

    @api.multi
    def _compute_attendees_count(self):
        for event in self:
            event.attendees_count = len(event.partner_ids)

    note = fields.Text("Internal Notes")
    attendees_count = fields.Integer(
        "Attendees", compute='_compute_attendees_count')
