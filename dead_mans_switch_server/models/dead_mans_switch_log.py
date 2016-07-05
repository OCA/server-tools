# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class DeadMansSwitchLog(models.Model):
    _name = 'dead.mans.switch.log'
    _description = 'Instance log line'
    _order = 'create_date desc'
    _rec_name = 'create_date'

    instance_id = fields.Many2one(
        'dead.mans.switch.instance', 'Instance', index=True)
    cpu = fields.Float('CPU', group_operator='avg')
    ram = fields.Float('RAM', group_operator='avg')
    user_count = fields.Integer('Users logged in', group_operator='avg')
