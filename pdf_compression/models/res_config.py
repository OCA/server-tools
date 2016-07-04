# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import SUPERUSER_ID, fields, models


class KnowledgeConfigSettings(models.TransientModel):
    _inherit = 'knowledge.config.settings'

    compression = fields.Selection([
        ('no', 'No Compression'),
        ('screen', 'SCREEN selects low-resolution output similar to the '
                   'Acrobat Distiller "Screen Optimized" setting'),
        ('ebook', 'EBOOK selects medium-resolution output similar to the '
                  'Acrobat Distiller "eBook" setting.'),
        ('printer', 'PRINTER selects output similar to the Acrobat'
                    'Distiller "Print Optimized" setting.'),
        ('prepress', 'PREPRESS selects output similar to Acrobat Distiller '
                     '"Prepress Optimized" setting.'),
        ('default', 'DEFAULT selects output intended to be useful across a '
                    'wide variety of uses, possibly at the expense of a '
                    'larger output file.')], 'PDF Compression',
        help='The Compression Level.',)

    pdfa_option = fields.Selection(
        string='PDF/A archiving',
        selection=[
            ('no', 'None'),
            ('pdfa1b', 'PDF/A-1b'),
            ('pdfa2b', 'PDF/A-2b')
        ],
        help="PDF/A is an ISO-standardized version of the Portable Document "
             "Format (PDF) specialized for the digital preservation of "
             "electronic documents.",)

    # compression
    def get_default_compression(
            self, cr, uid, ids, context=None):
        # API 8 is here not available because this function is called directly
        ir_values = self.pool.get('ir.values')
        compression = ir_values.get_default(
            cr, uid, 'ir.attachment', 'compression')
        return {
            'compression': compression,
        }

    def set_contract_set_defaults(self, cr, uid, ids, context=None):
        # API 8 is here not available because this function is called directly
        ir_values = self.pool.get('ir.values')
        config = self.browse(cr, uid, ids)[0]
        ir_values.set_default(cr, SUPERUSER_ID, 'ir.attachment', 'compression',
                              config.compression and config.compression or
                              False)

    # pdfa
    def get_default_pdfa_option(
            self, cr, uid, ids, context=None):
        # API 8 is here not available because this function is called directly
        ir_values = self.pool.get('ir.values')
        pdfa_option = ir_values.get_default(
            cr, uid, 'ir.attachment', 'pdfa_option')
        return {
            'pdfa_option': pdfa_option,
        }

    def set_contract_pdfa_option(self, cr, uid, ids, context=None):
        # API 8 is here not available because this function is called directly
        ir_values = self.pool.get('ir.values')
        config = self.browse(cr, uid, ids)[0]
        ir_values.set_default(cr, SUPERUSER_ID, 'ir.attachment', 'pdfa_option',
                              config.pdfa_option and config.pdfa_option or
                              False)
