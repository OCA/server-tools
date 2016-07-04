# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields
from openerp.models import Model


class IrActionsReportXml(Model):
    _inherit = 'ir.actions.report.xml'

    pdf_option = fields.Selection(
        string='PDF/A archiving',
        selection=[
            ('no', 'None'),
            ('default', 'Default PDF/A handling'),
            ('pdfa1b', 'PDF/A-1b'),
            ('pdfa2b', 'PDF/A-2b')
        ],
        help="PDF/A is an ISO-standardized version of the Portable Document "
             "Format (PDF) specialized for the digital preservation of "
             "electronic documents.",
        default='default')
