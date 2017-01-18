# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResUsersDevice(models.Model):
    _name = 'res.users.device'
    _description = 'Trusted Device for MFA Auth'

    user_id = fields.Many2one(
        comodel_name='res.users',
        ondelete='cascade',
        required=True,
    )
