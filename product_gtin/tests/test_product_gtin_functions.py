# -*- coding: utf-8 -*-
# #############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# it is not useful to use odoo unittest suite here as only
# methods without odoo tools are tested here.
import unittest2
import logging
_logger = logging.getLogger(__name__)

from openerp.addons.product_gtin import product_gtin


class TestIsPair(unittest2.TestCase):
    def test_returns(self):
        """Check the return of the function."""
        # http://en.wikipedia.org/wiki/Parity_of_zero
        self.assertTrue(product_gtin.is_pair(0))

        # Testing random numbers.
        self.assertTrue(product_gtin.is_pair(2))
        self.assertTrue(product_gtin.is_pair(4))
        self.assertTrue(product_gtin.is_pair(40))

        self.assertFalse(product_gtin.is_pair(1))
        self.assertFalse(product_gtin.is_pair(3))
        self.assertFalse(product_gtin.is_pair(5))
        self.assertFalse(product_gtin.is_pair(77))


VALID_EAN8_CODES = [
    # http://www.softmatic.com/barcode-ean-8.html
    "40123455",
    # http://www.barcodeisland.com/ean8.phtml
    "04210009",
]

VALID_EAN13_CODES = [
    # http://www.barcodeisland.com/ean13.phtml
    "0075678164125",
    "2000021262157",
]

VALID_UPC_CODES = [
    "012345678905",
    "080047440694",
    "123456789012",
]


class TestCheckUpc(unittest2.TestCase):
    """The codes have been tested against
    http://www.hipaaspace.com/Medical_Data_Validation/Universal_Product_Code/UPC_Validation.aspx  # noqa
    """
    def test_upc_codes(self):
        for code in VALID_UPC_CODES:
            _logger.debug('code: {}'.format(code))
            self.assertTrue(product_gtin.check_upc(code))

    def test_returns_wrong_upc_codes(self):
        self.assertFalse(product_gtin.check_upc(""))
        # test string
        self.assertFalse(product_gtin.check_upc("odoo_oca"))
        # less than 12 numbers
        self.assertFalse(product_gtin.check_upc("12345678901"))
        # 12 random numbers
        self.assertFalse(product_gtin.check_upc("123456789013"))
        # more than 12 numbers
        self.assertFalse(product_gtin.check_upc("12345678980123"))

    def test_ean8_codes(self):
        """Ean8 codes should not be valid for UPC."""
        for code in VALID_EAN8_CODES:
            _logger.debug('code: {}'.format(code))
            self.assertFalse(product_gtin.check_upc(code))

    def test_ean13_codes(self):
        """Ean13 codes should not be valid for UPC."""
        for code in VALID_EAN13_CODES:
            _logger.debug('code: {}'.format(code))
            self.assertFalse(product_gtin.check_upc(code))


class TestCheckEan8(unittest2.TestCase):

    def test_returns_earn8_codes(self):
        for code in VALID_EAN8_CODES:
            self.assertTrue(product_gtin.check_ean8(code))

    def test_returns_wrong_ean8_codes(self):
        self.assertFalse(product_gtin.check_ean8(""))
        # test string
        self.assertFalse(product_gtin.check_ean8("odoo_oca"))
        # less than 8 numbers
        self.assertFalse(product_gtin.check_ean8("1234567"))
        # 8 random numbers
        self.assertFalse(product_gtin.check_ean8("12345678"))
        self.assertFalse(product_gtin.check_ean8("82766678"))
        # 9 numbers
        self.assertFalse(product_gtin.check_ean8("123456789"))

    def test_return_ean8_codes(self):
        """Ean8 should not accept ean13"""
        for code in VALID_EAN13_CODES:
            self.assertFalse(product_gtin.check_ean8(code))

    def test_return_upc_codes(self):
        """Ean8 should not accept UPC"""
        for code in VALID_UPC_CODES:
            self.assertFalse(product_gtin.check_ean8(code))


class TestCheckEan13(unittest2.TestCase):

    def test_return_ean13_codes(self):
        """test valid ean 13 number."""
        for code in VALID_EAN13_CODES:
            self.assertTrue(product_gtin.check_ean13(code))

    def test_wrong_ean13_codes(self):
        self.assertFalse(product_gtin.check_ean13(""))
        # test string
        self.assertFalse(product_gtin.check_ean8("odoo_oca_sflx"))
        # less than 13 numbers
        self.assertFalse(product_gtin.check_ean13("123456789012"))
        # 13 random numbers
        self.assertFalse(product_gtin.check_ean13("1234567890123"))
        self.assertFalse(product_gtin.check_ean13("1234514728123"))
        # 14 numbers
        self.assertFalse(product_gtin.check_ean13("12345147281234"))

    def test_returns_ean8_codes(self):
        """Ean13 should not accept ean8"""
        for code in VALID_EAN8_CODES:
            self.assertFalse(product_gtin.check_ean13(code))

    def test_returns_upc_codes(self):
        """Ean13 should not accept UPC"""
        for code in VALID_UPC_CODES:
            self.assertFalse(product_gtin.check_ean13(code))


class TestCheckEan(unittest2.TestCase):

    def test_dict_check_ean(self):
        """Check if the dict DICT_CHECK_EAN exists."""
        self.assertTrue(product_gtin.DICT_CHECK_EAN)

    def test_dict_pair(self):
        self.assertEqual(
            product_gtin.DICT_CHECK_EAN[8], product_gtin.check_ean8
        )
        self.assertEqual(
            product_gtin.DICT_CHECK_EAN[12], product_gtin.check_upc
        )
        self.assertEqual(
            product_gtin.DICT_CHECK_EAN[13], product_gtin.check_ean13
        )
