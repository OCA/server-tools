# -*- coding: utf-8 -*-
# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase, at_install, post_install


@at_install(False)
@post_install(True)
class NameSearchCase(TransactionCase):

    def setUp(self):
        super(NameSearchCase, self).setUp()
        phone_field = self.env.ref('base.field_res_partner_phone')
        model_partner = self.env.ref('base.model_res_partner')
        model_partner.name_search_ids = phone_field
        self.Partner = self.env['res.partner']
        self.partner1 = self.Partner.create(
            {'name': 'Johann Gambolputty of Ulm',
             'phone': '+351 555 777'})
        self.partner2 = self.Partner.create(
            {'name': 'Luigi Verconti',
             'phone': '+351 777 555'})

    def test_NameSearchSearchWithSpaces(self):
        """Name Search Match full string, honoring spaces"""
        res = self.Partner.name_search('777 555')
        self.assertEqual(res[0][0], self.partner2.id)

    def test_NameSearchOrdered(self):
        """Name Search Match by words, honoring order"""
        res = self.Partner.name_search('johann ulm')
        # res is a list of tuples (id, name)
        self.assertEqual(res[0][0], self.partner1.id)

    def test_NameSearchUnordered(self):
        """Name Search Math by unordered words"""
        res = self.Partner.name_search('ulm gambol')
        self.assertEqual(res[0][0], self.partner1.id)

    def test_NameSearchMustMatchAllWords(self):
        """Name Search Must Match All Words"""
        res = self.Partner.name_search('ulm 555 777')
        self.assertFalse(res)
