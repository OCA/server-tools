# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestParser(TransactionCase):

    def test_getting_parser(self):
        expected_parser = [

            'name',
            'active',
            'credit_limit',
            'color',
            ('category_id', ['name']),
            ('country_id', ['name', 'code']),
            ('child_ids', [
                'name',
                'id',
                'email',
                ('country_id', ['name', 'code']),
                ('child_ids', ['name']),
            ]),
            'lang',
            'comment'
        ]

        exporter = self.env.ref('base_jsonify.ir_exp_partner')
        parser = exporter.get_json_parser()
        self.assertListEqual(parser, expected_parser)

        # modify an ir.exports_line to put an alias for a field
        self.env.ref('base_jsonify.category_id_name').write({
            'alias': 'category_id:category/name'
        })
        expected_parser[4] = ('category_id:category', ['name'])
        parser = exporter.get_json_parser()
        self.assertEqual(parser, expected_parser)

    def test_json_export(self):
        # Enforces TZ to validate the serialization result of a Datetime
        self.env.user.tz = "Europe/Brussels"
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
            ('category_id', ['name']),
            'create_date',
            'date',
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
            'date': fields.Date.from_string("2019-10-31")
        })
        self.env.cr.execute(
            "update res_partner set create_date=%s where id=%s",
            ("2019-10-31 14:39:49", partner.id),
        )
        partner.refresh()
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
            }],
            "create_date": "2019-10-31T15:39:49+01:00",
            "date": "2019-10-31",
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
