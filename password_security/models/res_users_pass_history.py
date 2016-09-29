# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import fields, models


class ResUsersPassHistory(models.Model):
    _name = 'res.users.pass.history'
    _description = 'Res Users Password History'

    _order = 'user_id, date desc'

    user_id = fields.Many2one(
        string='User',
        comodel_name='res.users',
        ondelete='cascade',
        index=True,
    )
    password_crypt = fields.Char(
        string='Encrypted Password',
    )
    date = fields.Datetime(
        default=lambda s: fields.Datetime.now(),
        index=True,
    )
