# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestBaseMerge(TransactionCase):

    def setUp(self):
        super(TestBaseMerge, self).setUp()
        partner_model = self.env['res.partner']
        country_model = self.env['res.country']
        # Introduce duplicate country records
        # purely by accident. All 4 countries
        # refer to the same country, supposedly.
        self.country01 = country_model.create({
            'name': 'Deep Space Nine',
            })
        self.country02 = country_model.create({
            'name': 'Deep Space Nine and a half',
            })
        self.country03 = country_model.create({
            'name': 'Deep Space Eight',
            })
        self.country04 = country_model.create({
            'name': 'Somewhere out in space',
            })
        # And assign these to different partners
        self.partner01 = partner_model.create({
            'name': 'George Partner',
            'customer': False,
            'is_company': False,
            'type': 'contact',
            'country_id': self.country01.id,
            })
        self.partner02 = partner_model.create({
            'name': 'Bill Partner',
            'customer': True,
            'is_company': False,
            'type': 'contact',
            'country_id': self.country02.id,
            })
        self.partner03 = partner_model.create({
            'name': 'Sam Partner',
            'customer': True,
            'is_company': False,
            'type': 'contact',
            'country_id': self.country03.id,
            })

    def test_merge(self):
        """ Test merging duplicate records """
        # Enable merging for res.country
        merge_record = self.env['base.merge.model'].create({
            'model_id': self.env['ir.model'].search([
                ('name', '=', 'Country')]).id,
        })
        # Ensure that display_name is correctly set
        self.assertEqual(
            merge_record.display_name,
            'Merging enabled for Country')
        # Check that action is created as needed
        action_id = self.env['ir.actions.act_window'].search([
            ('res_model', '=', 'base.merge.wizard'),
            ('src_model', '=', merge_record.model_id.model),
        ])
        self.assertTrue(action_id)
        self.assertEqual(merge_record.action_id, action_id)
        # Prepare source_ids
        # TODO: finish this
