# -*- encoding: utf-8 -*-
##############################################################################
# Copyright 2015 Pedro M. Baeza
# For license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class Report(models.Model):
    _inherit = 'report'

    @api.model
    def translate_doc(self, doc_id, model, lang_field, template, values):
        if self.env.context.get('force_lang'):
            obj = self.with_context(lang=self.env.context['force_lang'],
                                    translatable=True)
            return super(Report, obj).translate_doc(
                doc_id, model, lang_field, template, values)
