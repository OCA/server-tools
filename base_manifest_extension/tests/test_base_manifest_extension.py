# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
import tempfile
from openerp.tests.common import TransactionCase
from openerp.modules.module import load_information_from_description_file,\
    get_module_path, MANIFEST


class TestBaseManifestExtension(TransactionCase):
    def test_base_manifest_extension(self):
        # write a test manifest
        module_path = tempfile.mkdtemp(dir=os.path.join(
            get_module_path('base_manifest_extension'), 'static'
        ))
        with open(os.path.join(module_path, MANIFEST), 'w') as manifest:
            manifest.write(repr({
                'depends_if_installed': [
                    'base_manifest_extension',
                    'not installed',
                ],
            }))
        # parse it
        parsed = load_information_from_description_file(
            # this name won't really be used, but avoids a warning
            'base', mod_path=module_path,
        )
        self.assertIn('base_manifest_extension', parsed['depends'])
        self.assertNotIn('not installed', parsed['depends'])
        self.assertNotIn('depends_if_installed', parsed)
