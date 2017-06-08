# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Liu Lixia, Augustin Cisterne-Kaas
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
#############################################################################
import openerp.tests.common as common
from openerp.addons.connector.backend import Backend


@common.at_install(False)
@common.post_install(True)
class TestBackend(common.TransactionCase):
    """
    test generic Backend
    """

    def setUp(self):
        super(TestBackend, self).setUp()
        self.service = "dns"
        self.version = "1.7"

    def tearDown(self):
        super(TestBackend, self).tearDown()

    def test_dnspod(self):
        dnspod = Backend(self.service)
        self.assertEqual(dnspod.service, self.service)

    def test_child_dnspod(self):
        dnspod = Backend(self.service)
        child_dnspod = Backend(parent=dnspod, version=self.service)
        self.assertEqual(child_dnspod.service, dnspod.service)
