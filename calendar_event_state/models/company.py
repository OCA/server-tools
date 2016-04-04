# -*- coding: utf-8 -*-
# © 2016 Alessio Gerace - Agile Business Group
# © 2016 Lorenzo Battistini - Agile Business Group
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    calendar_state_ids = fields.One2many(
        'calendar.event.state', 'company_id', 'Events State')
