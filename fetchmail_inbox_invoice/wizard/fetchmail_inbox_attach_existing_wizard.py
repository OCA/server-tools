# coding: utf-8
# Copyright (C) 2014 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class FetchmailInboxAttachExistingWizard(models.TransientModel):
    _inherit = 'fetchmail.inbox.attach.existing.wizard'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        result = super(
            FetchmailInboxAttachExistingWizard, self).fields_view_get(
                view_id=view_id, view_type=view_type,
                toolbar=toolbar, submenu=submenu)
        if (self.env.context.get('default_mail_id') and
                self.env.context.get(
                    'set_default_res_model') == 'account.invoice'):
            mail = self.env['mail.message'].browse(
                self.env.context['default_mail_id'])
            result['fields']['res_id']['domain'] = [
                ('type', 'in', ('in_invoice', 'in_refund'))]
            result['fields']['res_id']['options'] = '{"no_create": True}'
            if mail.author_id:
                partner = mail.author_id.commercial_partner_id
                result['fields']['res_id']['context'].update(
                    search_default_partner_id=partner.id)
        return result
