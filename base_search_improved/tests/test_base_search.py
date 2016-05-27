# -*- coding: utf-8 -*-
# © 2016 Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class SomethingCase(TransactionCase):

    def test_SpaceReplacedByWildcard(self):
        """Space is replaced by a wildcard"""
        Partner = self.env['res.partner']
        # Johann Gambolputty  https://www.youtube.com/watch?v=UDPqB9i1ScY
        Partner.create(
            {'name': 'Johann Gambolputty de von Ausfern Hautkopft of Ulm'})
        res = Partner.search([('name', 'ilike', 'johann ausfern haut')])
        self.assertEqual(len(res), 1)
