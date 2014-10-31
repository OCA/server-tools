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

from openerp.tests.common import TransactionCase


class TestModuleRepository(TransactionCase):
    """Tests for 'Module Repository' Module"""

    def setUp(self):
        super(TestModuleRepository, self).setUp()
        self.imm_obj = self.registry('ir.module.module')

    # Test Section
    def test_01_module_update_list(self):
        """Test the correct process when the user click on 'update"""
        """ module list' button."""
        cr, uid = self.cr, self.uid
        self.imm_obj.update_list(cr, uid)
