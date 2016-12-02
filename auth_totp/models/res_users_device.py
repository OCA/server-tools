# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ResUsersDevice(models.Model):
    _name = 'res.users.device'
    _description = 'Trusted Device for MFA Auth'

    user_id = fields.Many2one(
        comodel_name='res.users',
        ondelete='cascade',
        required=True,
    )
