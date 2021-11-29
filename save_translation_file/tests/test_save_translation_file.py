# -*- coding: utf-8 -*-
# © 2016-TODAY Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os

from odoo.modules import get_module_path
from odoo.tools.misc import get_iso_codes
from odoo.tools.translate import load_language
import openerp.tests.common as common


class TestIrModuleModule(common.TransactionCase):

    def test_button_save_translation(self):

        load_language(self.cr, 'fr_FR')

        condition = [('name', '=', 'save_translation_file')]
        record = self.env['ir.module.module'].search(condition)
        record.button_save_translation()

        i18n_path = os.path.join(get_module_path(record.name), 'i18n')
        lang_obj = self.env['res.lang']
        condition = [('translatable', '=', True), ('code', '!=', 'en_US')]
        langs = lang_obj.search(condition)

        for lang in langs:
            iso_code = get_iso_codes(lang.code)
            path = os.path.join(i18n_path, '%s.po' % iso_code)
            self.assertEqual(os.path.isfile(path), True,
                             '%s.po must exists' % iso_code)
