# -*- coding: utf-8 -*-
# © 2015 Agile Business Group <http://www.agilebg.com>
# © 2015 Alessio Gerace <alesiso.gerace@agilebg.com>
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mock
import os
from datetime import datetime
from openerp.tests import common


class TestsAutoBackup(common.TransactionCase):

    def setUp(self):
        super(TestsAutoBackup, self).setUp()
        self.abk = self.env["db.backup"].create(
            {
                'name': u'Têst backup',
                'days_to_keep': 2,
            }
        )

    def test_local(self):
        """A local database is backed up."""
        filename = self.abk.filename(datetime.now())
        self.abk.action_backup()
        generated_backup = [f for f in os.listdir(self.abk.folder)
                            if f >= filename]
        self.assertEqual(len(generated_backup), 1)
        self.abk.action_backup()
        # here the cleanup must kick in and delete the first backup
        self.abk.action_backup()
        generated_backup = [f for f in os.listdir(self.abk.folder)
                            if f >= filename]
        self.assertEqual(len(generated_backup), 2)

    def test_remote(self):
        with mock.patch(
            'openerp.addons.auto_backup.models.db_backup.pysftp.Connection'
        ) as mock_connection:
            mock_contextmanager = mock.MagicMock()
            mock_connection.return_value = mock.MagicMock()
            mock_connection.return_value.__enter__.return_value =\
                mock_contextmanager
            mock_contextmanager.listdir.return_value = [
                '1.dump.zip', '2.dump.zip', '3.dump.zip',
            ]
            with mock_connection() as test:
                self.assertEqual(test, mock_contextmanager)
            self.abk.method = 'sftp'
            self.abk.action_backup()
            mock_contextmanager.unlink.assert_called_once()
