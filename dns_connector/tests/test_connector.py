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
from openerp.addons.connector.session import ConnectorSession
from ..connector import get_environment


@common.at_install(False)
@common.post_install(True)
class TestAddCheckPoint(common.TransactionCase):
    """
    test generic Backend
    """

    def setUp(self):
        super(TestAddCheckPoint, self).setUp()
        self.session = ConnectorSession(self.cr, self.uid)
        self.model_name = 'dns.domain'
        self.backend_id = 1

    def tearDown(self):
        super(TestAddCheckPoint, self).tearDown()

    def test_get_environment(self):
        """test get_environment"""
    	env = get_environment(self.session, self.model_name, self.backend_id)
    	self.assertEqual(self.model_name, env.model_name)
        self.assertEqual(self.session, env.session)
