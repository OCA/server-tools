# -*- coding: utf-8 -*-
# Copyright 2017 Avoin.Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class Paper(models.Model):
    _inherit = 'report.paperformat'

    custom_params = fields.One2many(
        'report.paperformat.parameter',
        'paperformat_id',
        'Custom Parameters',
        help='Custom Parameters passed forward as wkhtmltopdf '
             'command arguments'
    )

    @api.constrains('custom_params')
    def _check_recursion(self):
        for paperformat in self:
            sample_html = """
                <!DOCTYPE html>
                <html style="height: 0;">
                    <body>
                        <div>
                        <span itemprop="name">Hello World!</span>
                        </div>
                    </body>
                </html>
            """
            contenthtml = [tuple([1, sample_html])]
            content = self.env['report']._run_wkhtmltopdf(
                [], [], contenthtml, False, paperformat, False, False, False)
            if not content:
                raise ValidationError(_(
                    "Failed to create a PDF using the parameters provided"))
