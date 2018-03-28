# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os
import unittest

from .. import addon_hash
from ..models.module import DEFAULT_EXCLUDE_PATTERNS


class TestAddonHash(unittest.TestCase):

    def setUp(self):
        super(TestAddonHash, self).setUp()
        self.sample_dir = os.path.join(
            os.path.dirname(__file__),
            'sample_module',
        )

    def test_basic(self):
        files = list(addon_hash._walk(
            self.sample_dir,
            exclude_patterns=[],
            keep_langs=[],
        ))
        self.assertEqual(files, [
            'README.rst',
            'data/f1.xml',
            'data/f2.xml',
            'i18n/en.po',
            'i18n/en_US.po',
            'i18n/fr.po',
            'i18n/fr_BE.po',
            'i18n/test.pot',
            'i18n_extra/en.po',
            'i18n_extra/fr.po',
            'i18n_extra/nl_NL.po',
            'models/stuff.py',
            'models/stuff.pyc',
            'models/stuff.pyo',
            'static/src/some.js',
        ])

    def test_exclude(self):
        files = list(addon_hash._walk(
            self.sample_dir,
            exclude_patterns=DEFAULT_EXCLUDE_PATTERNS.split(','),
            keep_langs=['fr_FR', 'nl'],
        ))
        self.assertEqual(files, [
            'README.rst',
            'data/f1.xml',
            'data/f2.xml',
            'i18n/fr.po',
            'i18n/fr_BE.po',
            'i18n_extra/fr.po',
            'i18n_extra/nl_NL.po',
            'models/stuff.py',
        ])

    def test2(self):
        checksum = addon_hash.addon_hash(
            self.sample_dir,
            exclude_patterns=['*.pyc', '*.pyo', '*.pot', 'static/*'],
            keep_langs=['fr_FR', 'nl'],
        )
        self.assertEqual(checksum, 'fecb89486c8a29d1f760cbd01c1950f6e8421b14')
