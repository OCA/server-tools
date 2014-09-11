# -*- encoding: utf-8 -*-
##############################################################################
#
#    Tools - Repository of Modules for Odoo
#    Copyright (C) 2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

# from openerp.osv import osv
from openerp.tests.common import TransactionCase


class TestModuleRepository(TransactionCase):
    """Tests for 'Module Repository' Module"""

    def setUp(self):
        super(TestModuleRepository, self).setUp()
#        cr, uid = self.cr, self.uid
        self.imm_obj = self.registry('ir.module.module')
#        self.pp_obj = self.registry('product.product')
#        self.tg_obj = self.registry('tax.group')
#        self.wctg_obj = self.registry('wizard.change.tax.group')
#        self.main_company_id = self.imd_obj.get_object_reference(
#            cr, uid, 'base', 'main_company')[1]
#        self.tg1_id = self.imd_obj.get_object_reference(
#            cr, uid, 'product_taxes_group', 'tax_group_1')[1]
#        self.tg2_id = self.imd_obj.get_object_reference(
#            cr, uid, 'product_taxes_group', 'tax_group_2')[1]
#        self.pp1_id = self.imd_obj.get_object_reference(
#            cr, uid, 'product_taxes_group', 'product_product_1')[1]
#        self.at_purchase_1_id = self.imd_obj.get_object_reference(
#            cr, uid, 'product_taxes_group', 'account_tax_purchase_1')[1]
#        self.at_sale_1_id = self.imd_obj.get_object_reference(
#            cr, uid, 'product_taxes_group', 'account_tax_sale_1')[1]
#        self.at_sale_2_id = self.imd_obj.get_object_reference(
#            cr, uid, 'product_taxes_group', 'account_tax_sale_2')[1]

    # Test Section
    def test_01_module_update_list(self):
        """Test the correct process when the user click on 'update"""
        """ module list' button."""
        cr, uid = self.cr, self.uid
        self.imm_obj.update_list(cr, uid)

#    def test_02_check_coherent_vals_tax_group_exist(self):
#        """Test if the behaviour of the function product.template
#        check_coherent_vals() when the combination exist."""
#        cr, uid = self.cr, self.uid
#        vals = {
#            'name': 'Product Product Name',
#            'company_id': self.main_company_id,
#            'supplier_taxes_id': [self.at_purchase_1_id],
#            'taxes_id': [self.at_sale_1_id, self.at_sale_2_id],
#        }
#        pp_id = self.pp_obj.create(cr, uid, vals)
#        pp = self.pp_obj.browse(cr, uid, pp_id)
#        self.assertEqual(
#            pp.tax_group_id.id, self.tg1_id,
#            "Recovery of Correct Tax Group failed during creation.")
#        vals = {
#            'supplier_taxes_id': [[6, 0, []]],
#            'taxes_id': [[6, 0, [self.at_sale_2_id]]],
#        }
#        self.pp_obj.write(cr, uid, pp_id, vals)
#        pp = self.pp_obj.browse(cr, uid, pp_id)
#        self.assertEqual(
#            pp.tax_group_id.id, self.tg2_id,
#            "Recovery of Correct Tax Group failed during update.")

#    def test_03_check_coherent_vals_tax_group_doesnt_exist(self):
#        """Test if the behaviour of the function product.template
#        check_coherent_vals() when the combination doesn't exist."""
#        cr, uid = self.cr, self.uid
#        vals = {
#            'name': 'Product Product Name',
#            'company_id': self.main_company_id,
#            'supplier_taxes_id': [self.at_purchase_1_id],
#            'taxes_id': [self.at_sale_1_id],
#        }
#        count_1 = len(self.tg_obj.search(cr, uid, []))
#        self.pp_obj.create(cr, uid, vals)
#        count_2 = len(self.tg_obj.search(cr, uid, []))
#        self.assertEqual(
#            count_1 + 1, count_2,
#            "New combination must create new Tax Group.")

#    def test_04_update_tax_group(self):
#        """Test if changing a Tax Group change the product."""
#        cr, uid = self.cr, self.uid
#        self.tg_obj.write(cr, uid, [self.tg1_id], {
#            'customer_tax_ids': [[6, 0, [self.at_sale_1_id]]]})
#        pp = self.pp_obj.browse(cr, uid, self.pp1_id)
#        self.assertEqual(
#            [
#                [x.id for x in pp.taxes_id],
#                [x.id for x in pp.supplier_taxes_id]],
#            [[self.at_sale_1_id], [self.at_purchase_1_id]],
#            "Update taxes in Tax Group must update associated Products.")

#    def test_05_unlink_tax_group(self):
#        """Test if unlinking a Tax Group with product fails."""
#        cr, uid = self.cr, self.uid
#        try:
#            self.tg_obj.unlink(cr, uid, [self.tg1_id])
#        except osv.except_osv:
#            error = True
#        self.assertEquals(
#            error, True, "Unlinking Tax Group with Products must fails!")
