# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestParser(TransactionCase):

    def test_getting_parser(self):
        expected_parser = [
            u'active',
            (u'category_id', [u'name']),
            (u'child_ids', [(
                u'child_ids', [u'name']),
                (u'country_id', [u'code', u'name']),
                u'email', u'id',
                u'name'
            ]),
            u'color',
            u'comment',
            (u'country_id', [u'code', u'name']),
            u'credit_limit',
            u'lang',
            u'name']

        exporter = self.env.ref('base_jsonify.ir_exp_partner')
        parser = exporter.get_json_parser()
        self.assertEqual(parser, expected_parser)

        # modify an ir.exports_line to put an alias for a field
        self.env.ref('base_jsonify.category_id_name').write({
            'alias': 'category_id:category/name'
        })
        expected_parser[1] = (u'category_id:category', [u'name'])
        parser = exporter.get_json_parser()
        self.assertEqual(parser, expected_parser)

    def test_json_export(self):
        parser = [
            u'lang',
            u'comment',
            u'credit_limit',
            u'name',
            u'color',
            (u'child_ids:children', [
                (u'child_ids:children', [u'name']),
                u'email',
                (u'country_id:country', [u'code', u'name']),
                u'name',
                u'id',
            ]),
            (u'country_id:country', [u'code', u'name']),
            u'active',
            (u'category_id', [u'name'])
        ]
        partner = self.env['res.partner'].create({
            'name': 'Akretion',
            'country_id': self.env.ref('base.fr').id,
            'lang': 'en_US', # default
            'category_id': [(0, 0, {'name': 'Inovator'})],
            'child_ids': [
                (0, 0, {
                    'name': 'Sebatien Beau',
                    'country_id': self.env.ref('base.fr').id
                })
            ],
        })
        expected_json = {
            u'lang': u'en_US',
            u'comment': None,
            u'credit_limit': 0.0,
            u'name': u'Akretion',
            u'color': 0,
            u'country': {
                u'code': u'FR',
                u'name': u'France'
            },
            u'active': True,
            u'category_id': [
                {u'name': u'Inovator'}
            ],
            u'children': [{
                u'id': partner.child_ids.id,
                u'country': {
                    u'code': u'FR',
                    u'name': u'France'
                },
                u'children': [],
                u'name': u'Sebatien Beau',
                u'email': None
            }]
        }
        json_partner = partner.jsonify(parser)

        self.assertDictEqual(json_partner[0], expected_json)

        json_partner = partner.jsonify(parser)

        self.assertDictEqual(json_partner[0], expected_json)

        # Check that only boolean fields have boolean values into json
        # By default if a field is not set into Odoo, the value is always False
        # This value is not the expected one into the json
        partner.write({'child_ids': [(6, 0, [])],
                       'active': False,
                       'lang': False})
        json_partner = partner.jsonify(parser)
        expected_json['active'] = False
        expected_json['lang'] = None
        expected_json['children'] = []
        self.assertDictEqual(json_partner[0], expected_json)
