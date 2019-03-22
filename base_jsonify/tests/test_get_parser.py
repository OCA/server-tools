# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestParser(TransactionCase):

    def test_getting_parser(self):
        expected_parser = [
            'active',
            ('category_id', ['name']),
            ('child_ids', [(
                'child_ids', ['name']),
                ('country_id', ['code', 'name']),
                'email', 'id',
                'name'
            ]),
            'color',
            'comment',
            ('country_id', ['code', 'name']),
            'credit_limit',
            'lang',
            'name']

        exporter = self.env.ref('base_jsonify.ir_exp_partner')
        parser = exporter.get_json_parser()
        self.assertEqual(parser, expected_parser)

        # modify an ir.exports_line to put an alias for a field
        self.env.ref('base_jsonify.category_id_name').write({
            'alias': 'category_id:category/name'
        })
        expected_parser[1] = ('category_id:category', ['name'])
        parser = exporter.get_json_parser()
        self.assertEqual(parser, expected_parser)

    def test_json_export(self):
        parser = [
            'lang',
            'comment',
            'credit_limit',
            'name',
            'color',
            ('child_ids:children', [
                ('child_ids:children', ['name']),
                'email',
                ('country_id:country', ['code', 'name']),
                'name',
                'id',
            ]),
            ('country_id:country', ['code', 'name']),
            'active',
            ('category_id', ['name'])
        ]
        partner = self.env['res.partner'].create({
            'name': 'Akretion',
            'country_id': self.env.ref('base.fr').id,
            'lang': 'en_US',  # default
            'category_id': [(0, 0, {'name': 'Inovator'})],
            'child_ids': [
                (0, 0, {
                    'name': 'Sebatien Beau',
                    'country_id': self.env.ref('base.fr').id
                })
            ],
        })
        expected_json = {
            'lang': 'en_US',
            'comment': None,
            'credit_limit': 0.0,
            'name': 'Akretion',
            'color': 0,
            'country': {
                'code': 'FR',
                'name': 'France'
            },
            'active': True,
            'category_id': [
                {'name': 'Inovator'}
            ],
            'children': [{
                'id': partner.child_ids.id,
                'country': {
                    'code': 'FR',
                    'name': 'France'
                },
                'children': [],
                'name': 'Sebatien Beau',
                'email': None
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
