# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class EphemeralFieldTester(models.Model):
    _name = 'ephemeral.field.tester'
    _description = 'Ephemeral Field Tester'

    control = fields.Char(
        help='This is the control field.',
    )
