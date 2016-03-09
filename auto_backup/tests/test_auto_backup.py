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

import os
from datetime import datetime
from openerp.tests import common


class TestsAutoBackup(common.TransactionCase):

    def setUp(self):
        super(TestsAutoBackup, self).setUp()
        self.abk = self.env["db.backup"].create(
            {
                'name': u'Têst backup',
            }
        )

    def test_local(self):
        """A local database is backed up."""
        filename = self.abk.filename(datetime.now())
        self.abk.action_backup()
        generated_backup = [f for f in os.listdir(self.abk.folder)
                            if f >= filename]
        self.assertEqual(len(generated_backup), 1)
