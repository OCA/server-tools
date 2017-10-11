# -*- coding: utf-8 -*-
# Copyright 2017 Kaushal Prajapati <kbprajapati@live.com>.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    password_expiration = fields.Integer(
        'Days',
        default=60,
        help='How many days until passwords expire',
    )
    password_length = fields.Integer(
        'Characters',
        default=12,
        help='Minimum number of characters',
    )
    password_lower = fields.Integer(
        'Lowercase',
        help='Require lowercase letters',
    )
    password_upper = fields.Integer(
        'Uppercase',
        help='Require uppercase letters',
    )
    password_numeric = fields.Integer(
        'Numeric',
        help='Require numeric digits',
    )
    password_special = fields.Integer(
        'Special',
        help='Require unique special characters',
    )
    password_history = fields.Integer(
        'History',
        default=30,
        help='Disallow reuse of this many previous passwords - use negative '
             'number for infinite, or 0 to disable',
    )
    password_minimum = fields.Integer(
        'Minimum Hours',
        default=24,
        help='Amount of hours until a user may change password again',
    )
