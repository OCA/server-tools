# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import TransactionCase, at_install, post_install


@at_install(False)
@post_install(True)
class TestBaseTrigramIndex(TransactionCase):

    def setUp(self):
        super(TestBaseTrigramIndex, self).setUp()
        self.ResPartner = self.env['res.partner']
        self.TrgmIndex = self.env['trgm.index']

    def test_create_index(self):
        """Test the creation of the index."""
        if (self.TrgmIndex._trgm_extension_exists() != 'installed' or
                self.TrgmIndex.index_exists('res.partner', 'name')):
            return

        field_partner_name = self.env.ref('base.field_res_partner_name')
        self.TrgmIndex.create({
            'field_id': field_partner_name.id,
            'index_type': 'gin',
        })

        table_name = self.ResPartner._table
        column_name = field_partner_name.name
        index_type = 'gin'
        index_name = '%s_%s_idx' % (column_name, index_type)
        index_exists, index_name = self.TrgmIndex.get_not_used_index(
            index_name, table_name)
        self.assertTrue(index_exists)
