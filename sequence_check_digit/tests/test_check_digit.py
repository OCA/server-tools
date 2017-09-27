# -*- coding: utf-8 -*-
# Copyright 2017 Creu Blanca <https://creublanca.es/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common
import logging
from odoo.exceptions import ValidationError
try:
    from stdnum.iso7064 import mod_97_10
    from stdnum.iso7064 import mod_37_2, mod_37_36
    from stdnum.iso7064 import mod_11_2, mod_11_10
    from stdnum import luhn, damm, verhoeff
except(ImportError, IOError) as err:
    logging.info(err)


class TestSequenceCheckDigit(common.TransactionCase):

    def test_check_digit(self):
        sequence_obj = self.env['ir.sequence']
        sequence = sequence_obj.create({
            'name': 'Test sequence',
            'implementation': 'standard',
            'check_digit_formula': 'none',
            'padding': '5'
        })
        sequence.check_digit_formula = 'luhn'
        self.assertTrue(luhn.validate(sequence.next_by_id()))
        sequence.check_digit_formula = 'damm'
        self.assertTrue(damm.validate(sequence.next_by_id()))
        sequence.check_digit_formula = 'verhoeff'
        self.assertTrue(verhoeff.validate(sequence.next_by_id()))
        sequence.check_digit_formula = 'ISO7064_11_2'
        self.assertTrue(mod_11_2.validate(sequence.next_by_id()))
        sequence.check_digit_formula = 'ISO7064_11_10'
        self.assertTrue(mod_11_10.validate(sequence.next_by_id()))
        with self.assertRaises(ValidationError):
            sequence.prefix = 'A'
        sequence.prefix = ''
        sequence.check_digit_formula = 'ISO7064_37_2'
        sequence.prefix = 'A'
        self.assertTrue(mod_37_2.validate(sequence.next_by_id()))
        sequence.check_digit_formula = 'ISO7064_37_36'
        self.assertTrue(mod_37_36.validate(sequence.next_by_id()))
        sequence.check_digit_formula = 'ISO7064_97_10'
        self.assertTrue(mod_97_10.validate(sequence.next_by_id()))
