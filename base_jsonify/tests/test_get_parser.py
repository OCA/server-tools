# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestParser(TransactionCase):

    def setUp(self):
        super(TestParser, self).setUp()
        self.expected_parser = [
            u'lang',
            u'comment',
            u'credit_limit',
            u'name',
            u'color',
            (u'child_ids', [
                (u'child_ids', [u'name']),
                u'email',
                (u'country_id', [u'code', u'name']),
                u'name',
                u'id',
                ]),
            (u'country_id', [u'code', u'name']),
            u'active',
            (u'category_id', [u'name'])
        ]

    def test_getting_parser(self):
        exporter = self.env.ref('base_jsonify.ir_exp_partner')
        parser = exporter.get_json_parser()
        self.assertEqual(parser, self.expected_parser)

    def test_json_export(self):
        expected_json = [{
            u'lang': False,
            u'comment': False,
            u'credit_limit': 0.0,
            u'name': u'Camptocamp',
            u'color': 0,
            u'country_id': {u'code': u'FR', u'name': u'France'},
            u'child_ids': [{
                u'id': 29,
                u'country_id': {
                    u'code': u'FR',
                    u'name': u'France'
                    },
                u'child_ids': [],
                u'email': u'ayaan.agarwal@bestdesigners.example.com',
                u'name': u'Ayaan Agarwal'
            }, {
                u'id': 35,
                u'country_id': {
                    u'code': u'FR',
                    u'name': u'France'},
                u'child_ids': [],
                u'email': u'benjamin.flores@nebula.example.com',
                u'name': u'Benjamin Flores'
            }, {
                u'id': 28,
                u'country_id': {
                    u'code': u'FR',
                    u'name': u'France'},
                u'child_ids': [],
                u'email': u'phillipp.miller@mediapole.example.com',
                u'name': u'Phillipp Miller'
            }],
            u'active': True,
            u'category_id': [
                {u'name': u'Gold'},
                {u'name': u'Services'}
            ]
        }]
        partner = self.env.ref('base.res_partner_12')
        json_partner = partner.jsonify(self.expected_parser)
        self.assertEqual(json_partner, expected_json)
