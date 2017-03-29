# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields


class EphemeralChar(fields.Char):

    def convert_to_write(self, value, target=None, fnames=None):
        """ Always return False in order to not save to database. """
        return False
