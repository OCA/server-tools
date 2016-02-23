# coding: utf-8
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class fetchmail_server(models.Model):
    _inherit = 'fetchmail.server'

    @api.model
    def get_file_type(self):
        return []

    @api.model
    def _get_file_type(self):
        return self.get_file_type()

    def company_default_get(self):
        company_id = (self.env['res.company'].
                      _company_default_get('fetchmail.server'))
        return self.env['res.company'].browse(company_id)

    file_type = fields.Selection(
        selection='_get_file_type',
        help='The file type will show some special option')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=company_default_get
        )  # Why this field do not exist by default?
    attachment_metadata_condition_ids = fields.One2many(
        'ir.attachment.metadata.condition', 'server_id', string='Attachment')

    @api.one
    def get_context_for_server(self):
        if self._context is None:
            ctx = {}
        else:
            ctx = self._context.copy()
        ctx['default_attachment_metadata_vals'] = {}
        ctx['default_company_id'] = self.company_id.id
        ctx['default_fetchmail_server_id'] = self.id
        return ctx

    @api.multi
    def fetch_mail(self):
        for server in self:
            super(fetchmail_server, server).fetch_mail()
        return True
