# Copyright 2016 Therp BV <http://therp.nl>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from lxml import etree
from odoo.tests.common import TransactionCase


class TestBaseViewInheritanceExtension(TransactionCase):

    def test_base_view_inheritance_extension(self):
        view_id = self.env.ref('base.view_partner_simple_form').id
        fields_view_get = self.env['res.partner'].fields_view_get(
            view_id=view_id
        )
        view = etree.fromstring(fields_view_get['arch'])
        # verify normal attributes work
        self.assertEqual(view.xpath('//form')[0].get('string'), 'Partner form')
        # verify our extra context key worked
        self.assertTrue(
            'default_name' in
            view.xpath('//field[@name="parent_id"]')[0].get('context')
        )
        self.assertTrue(
            "context.get('company_id', context.get('company'))" in
            view.xpath('//field[@name="parent_id"]')[0].get('context')
        )
