# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
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
    password_lower = fields.Boolean(
        'Lowercase',
        default=True,
        help='Require lowercase letters',
    )
    password_upper = fields.Boolean(
        'Uppercase',
        default=True,
        help='Require uppercase letters',
    )
    password_numeric = fields.Boolean(
        'Numeric',
        default=True,
        help='Require numeric digits',
    )
    password_special = fields.Boolean(
        'Special',
        default=True,
        help='Require special characters',
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
