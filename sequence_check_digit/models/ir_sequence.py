# -*- coding: utf-8 -*-
# Copyright (C) 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging
try:
    from stdnum.iso7064 import mod_97_10
    from stdnum.iso7064 import mod_37_2, mod_37_36
    from stdnum.iso7064 import mod_11_2, mod_11_10
    from stdnum import luhn, damm, verhoeff
except(ImportError, IOError) as err:
    logging.info(err)


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    check_digit_formula = fields.Selection(
        selection=[
            ('none', 'None'),
            ('luhn', 'Luhn'),
            ('damm', 'Damm'),
            ('verhoeff', 'Verhoeff'),
            ('ISO7064_11_2', 'ISO 7064 Mod 11, 2'),
            ('ISO7064_11_10', 'ISO 7064 Mod 11, 10'),
            ('ISO7064_37_2', 'ISO 7064 Mod 37, 2'),
            ('ISO7064_37_36', 'ISO 7064 Mod 37, 36'),
            ('ISO7064_97_10', 'ISO 7064 Mod 97, 10'),
        ], default='none'
    )

    @api.constrains('check_digit_formula', 'prefix', 'suffix')
    def check_check_digit_formula(self):
        try:
            self.get_next_char(0)
        except Exception:
            raise ValidationError(_('Format is not accepted'))

    def get_check_digit(self, code):
        if self.check_digit_formula == 'none':
            return ''
        try:
            if self.check_digit_formula == 'luhn':
                return luhn.calc_check_digit(code)
            if self.check_digit_formula == 'damm':
                return damm.calc_check_digit(code)
            if self.check_digit_formula == 'verhoeff':
                return verhoeff.calc_check_digit(code)
            if self.check_digit_formula == 'ISO7064_11_2':
                return mod_11_2.calc_check_digit(code)
            if self.check_digit_formula == 'ISO7064_11_10':
                return mod_11_10.calc_check_digit(code)
            if self.check_digit_formula == 'ISO7064_37_2':
                return mod_37_2.calc_check_digit(code)
            if self.check_digit_formula == 'ISO7064_37_36':
                return mod_37_36.calc_check_digit(code)
            if self.check_digit_formula == 'ISO7064_97_10':
                return mod_97_10.calc_check_digits(code)
            raise ValidationError(_('Function not found'))
        except Exception:
            raise ValidationError(_('Format is not accepted'))

    def get_next_char(self, number_next):
        code = super(IrSequence, self).get_next_char(number_next)
        if not self.check_digit_formula:
            return code
        return code + self.get_check_digit(code)
