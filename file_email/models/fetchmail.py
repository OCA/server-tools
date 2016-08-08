# coding: utf-8
#   @author Sébastien BEAU @ Akretion
#   @author Florian DA COSTA @ Akretion
#   @author Benoit GUILLOT @ Akretion
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    def company_default_get(self):
        company_id = (self.env['res.company'].
                      _company_default_get('fetchmail.server'))
        return self.env['res.company'].browse(company_id).id

    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=company_default_get)
    attachment_metadata_condition_ids = fields.One2many(
        'fetchmail.attachment.condition', 'server_id', string='Attachment')

    @api.multi
    def get_context_for_server(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx['default_fetchmail_server_id'] = self.id
        ctx['default_file_document_vals'] = {}
        return ctx

    @api.multi
    def fetch_mail(self):
        for server in self:
            ctx= server.get_context_for_server()
            super(FetchmailServer, server.with_context(ctx)).fetch_mail()
        return True


class FetchmailAttachmentCondition(models.Model):
    _name = 'fetchmail.attachment.condition'
    _description = "Fetchmail Attachment Conditions"

    name = fields.Char(string='Name', required=True,)
    from_email = fields.Char(string='Email')
    mail_subject = fields.Char()
    type = fields.Selection(
        selection=[('normal', 'Normal')],
        required=True, default='normal',
        help="Create your own type if the normal type "
             "do not correspond to your need")
    file_extension = fields.Char(
        required=True,
        help="File extension or file name")
    server_id = fields.Many2one('fetchmail.server', string='Server Mail')
    file_type = fields.Selection(
        selection=[],
        help='The file type will show some special option')
