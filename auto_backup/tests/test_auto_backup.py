# -*- coding: utf-8 -*-
# © 2015 Agile Business Group <http://www.agilebg.com>
# © 2015 Alessio Gerace <alesiso.gerace@agilebg.com>
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
from datetime import datetime
from openerp.tests import common
from openerp import exceptions, tools


class TestsAutoBackup(common.TransactionCase):

    def setUp(self):
        super(TestsAutoBackup, self).setUp()

    def new_record(self, method='sftp'):
        vals = {
            'name': u'Têst backup',
            'method': method,
        }
        if method == 'sftp':
            vals.update({
                'sftp_host': 'test_host',
                'sftp_port': '222',
                'sftp_user': 'tuser',
            })
        self.vals = vals
        self.env["db.backup"].create(vals) 

    def test_local(self):
        """A local database is backed up."""
        rec_id = self.new_record('local')
        filename = rec_id.filename(datetime.now())
        rec_id.action_backup()
        generated_backup = [f for f in os.listdir(rec_id.folder)
                            if f >= filename]
        self.assertEqual(1, len(generated_backup))

    def test_compute_name_sftp(self):
        """ It should create proper SFTP URI """
        rec_id = self.new_record()
        self.assertEqual(
            'sftp://%(user)@%(host):%(port)%(folder)' % {
                'user': self.vals['sftp_user'],
                'host': self.vals['sftp_host'],
                'port': self.vals['sftp_port'],
                'folder': self.vals['folder'],
            },
            rec_id.name,
        )

    def test_check_folder(self):
        """ It should not allow recursive backups """
        rec_id = self.new_record()
        with self.assertRaises(exceptions.ValidationError):
            rec_id.write({
                'folder': '%s/another/path' % tools.config.filestore(
                    self.env.cr.dbname
                ),
            })
