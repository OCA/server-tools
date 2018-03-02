# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os
import tempfile

from openerp.modules import get_module_path
from openerp.tests.common import TransactionCase

_logger = logging.getLogger(__name__)
try:
    from checksumdir import dirhash
except ImportError:
    _logger.debug('Cannot `import checksumdir`.')


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()
        module_name = 'module_checksum_upgrade'
        self.own_module = self.env['ir.module.module'].search([
            ('name', '=', module_name),
        ])
        self.own_dir_path = get_module_path(module_name)
        self.own_checksum = dirhash(
            self.own_dir_path,
            'sha1',
            excluded_extensions=['pyc', 'pyo'],
        )
        self.own_writeable = os.access(self.own_dir_path, os.W_OK)

    def test_compute_checksum_dir(self):
        """It should compute the directory's SHA-1 hash"""
        self.assertEqual(
            self.own_module._get_checksum_dir(), self.own_checksum,
            'Module directory checksum not computed properly',
        )

    def test_compute_checksum_dir_ignore_excluded(self):
        """It should exclude .pyc/.pyo extensions from checksum
        calculations"""
        if not self.own_writeable:
            self.skipTest("Own directory not writeable")
        with tempfile.NamedTemporaryFile(suffix='.pyc', dir=self.own_dir_path):
            self.assertEqual(
                self.own_module._get_checksum_dir(), self.own_checksum,
                'SHA1 checksum does not ignore excluded extensions',
            )

    def test_compute_checksum_dir_recomputes_when_file_added(self):
        """It should return a different value when a non-.pyc/.pyo file is
        added to the module directory"""
        if not self.own_writeable:
            self.skipTest("Own directory not writeable")
        with tempfile.NamedTemporaryFile(suffix='.py', dir=self.own_dir_path):
            self.assertNotEqual(
                self.own_module._get_checksum_dir(), self.own_checksum,
                'SHA1 checksum not recomputed',
            )

    def test_saved_checksums(self):
        Imm = self.env['ir.module.module']
        base_module = Imm.search([('name', '=', 'base')])
        self.assertEqual(base_module.state, 'installed')
        self.assertFalse(Imm._get_saved_checksums())
        Imm._save_installed_checksums()
        saved_checksums = Imm._get_saved_checksums()
        self.assertTrue(saved_checksums)
        self.assertTrue(saved_checksums['base'])
