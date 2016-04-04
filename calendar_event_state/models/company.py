# -*- coding: utf-8 -*-
# Copyright 2016 Alessio Gerace - Agile Business Group
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    calendar_state_ids = fields.One2many(
        'calendar.event.state', 'company_id', 'Events State')
