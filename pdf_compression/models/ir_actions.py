# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015 bloopark systems (<http://bloopark.de>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
