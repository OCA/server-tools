# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Agile Business Group <http://www.agilebg.com>
#    Copyright (C) 2015 Alessio Gerace <alesiso.gerace@agilebg.com>
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

from openerp.tests import common
from openerp.exceptions import except_orm


class TestsAutoBackup(common.TransactionCase):

    def setUp(self):
        super(TestsAutoBackup, self).setUp()
        self.abk_model = self.env["db.backup"]
        self.cron_model = self.env["ir.cron"]

    def test_0(self):
        with self.assertRaises(except_orm):
            self.abk_model.create({'name': 'abcd', 'adminpassword': 'admin'})

    def test_1(self):
        this = self.abk_model.create(
            {
                'bkp_dir': '/tmp',
                'adminpassword': 'admin'
            }
        )
        self.assertEqual(this.host, 'localhost')
