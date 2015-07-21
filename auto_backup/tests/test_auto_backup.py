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

import base64
from openerp.tests import common
from openerp.exceptions import except_orm, Warning
from openerp.modules.module import get_module_resource
import os
import time
from datetime import datetime, date, timedelta

class TestsAutoBackup(common.TransactionCase):

    def setUp(self):
        super(TestsAutoBackup, self).setUp()
        self.abk_model = self.env["db.backup"]
        self.cron_model = self.env["ir.cron"]


    def test_0(self):
        with self.assertRaises(except_orm):
            self.abk_model.create({'name': 'abcd'})

    def test_1(self):
        this = self.abk_model.create(
            {
                'bkp_dir': '/tmp'
            }
        )
        self.assertEqual(this.host, 'localhost')
        cronbk = self.cron_model.search([('name', '=', 'Backup scheduler')])
        import pdb;pdb.set_trace()
        cronbk.write(
            {
                'active': True,
                'doall': True
            }
        )
        filetime = (
            datetime.now() + timedelta(minutes=1)
        ).strftime('%d_%m_%Y_%H_%M_%S')

        bkp_file = '%s_%s.dimp.zip' % (
            filetime, this.name)
        file_path = os.path.join(this.bkp_dir, bkp_file)
        self.assertEqual(os.path.isfile(file_path), True)
