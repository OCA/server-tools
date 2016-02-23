# -*- coding: utf-8 -*-
# © 2016-TODAY Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
from openerp import models, fields, api, tools, _
from openerp.modules import get_module_path
from openerp.tools.misc import get_iso_codes
from openerp.exceptions import Warning
import polib

format_ = 'po'
class translate_module(models.TransientModel):
    _name = 'translate.module'
    
    
    def _get_language(self):
        lang_model = self.env['res.lang']
        lang_ids = lang_model.search([('translatable', '=', True),('code', '!=', 'en_US')])
        languages = []
        for lang in lang_ids:
            languages.append((lang.code,lang.name))
        return languages

    
    module = fields.Many2one('ir.module.module','Module')
    lang = fields.Selection(_get_language, string='Language')
    translate_module_terms = fields.One2many('translate.module.terms','translate_module_id','Translated Terms')
    
    @api.onchange('module','lang')
    def onchange_module_lang(self):
        if self.module and self.lang:
            i18n_path = os.path.join(get_module_path(self.module.name), 'i18n')
            if not os.path.isdir(i18n_path):
                self.env['ir.module.module'].browse(self.module.id).button_save_translation()
            
            iso_code = get_iso_codes(self.lang)
            filename = '%s.%s' % (iso_code, format_)
            path = os.path.join(i18n_path, filename)
            if not os.path.isfile(path):
                self.env['ir.module.module'].browse(self.module.id).button_save_translation()
            po = polib.pofile(path) 
            translated_terms  = []
            for entry in po:
                translated_terms.append({'original_term' : entry.msgid, 'translated_value':entry.msgstr})
            self.translate_module_terms = translated_terms
            
    @api.one        
    def save_translated_file(self):
        if len(self.translate_module_terms) and self.module and self.lang:
            i18n_path = os.path.join(get_module_path(self.module.name), 'i18n')
            iso_code = get_iso_codes(self.lang)
            filename = '%s.%s' % (iso_code, format_)
            path = os.path.join(i18n_path, filename)
            po = polib.pofile(path)
            for term in self.translate_module_terms:
                #search for term in .po file
                entry = po.find(term.original_term)
                #if found update po file
                if entry:
                    entry.msgstr = term.translated_value
            po.save()
            return True
        
            
           
                
class trnaslate_module_terms(models.TransientModel):
    _name = 'translate.module.terms'
    translate_module_id = fields.Many2one('translate.module', 'Translate Module', ondelete='cascade')
    original_term = fields.Char('Origin Term')
    translated_value = fields.Char('Translated Term')
    
    
