# -*- coding: utf-8 -*-
# © 2016-TODAY Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os

from odoo import models, api, tools
from odoo.modules import get_module_path
from odoo.tools.misc import get_iso_codes


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.one
    def button_save_translation(self):

        format_ = 'po'

        i18n_path = os.path.join(get_module_path(self.name), 'i18n')
        if not os.path.isdir(i18n_path):
            os.mkdir(i18n_path)

        lang_obj = self.env['res.lang']
        condition = [('translatable', '=', True), ('code', '!=', 'en_US')]
        langs = lang_obj.search(condition)

        files = [('%s.pot' % self.name, False)]
        for lang in langs:
            iso_code = get_iso_codes(lang.code)
            filename = '%s.%s' % (iso_code, format_)
            files.append((filename, lang.code))

        for filename, lang in files:
            path = os.path.join(i18n_path, filename)
            with open(path, 'w') as buf:
                tools.trans_export(lang, [self.name], buf, format_,
                                   self.env.cr)

        return True
