# -*- coding: utf-8 -*-
# © 2015 Agile Business Group <http://www.agilebg.com>
# © 2015 Alessio Gerace <alesiso.gerace@agilebg.com>
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
