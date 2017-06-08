# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mail_footer_notified_partners,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mail_footer_notified_partners is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     mail_footer_notified_partners is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with mail_footer_notified_partners.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api
from openerp import tools
from openerp.tools.translate import _


class MailNotification(models.Model):

    _inherit = 'mail.notification'

    @api.model
    def get_signature_footer(
            self, user_id, res_model=None, res_id=None, user_signature=True):
        """
        Override this method to add name of notified partners into the mail
        footer
        """
        footer = super(MailNotification, self).get_signature_footer(
            user_id, res_model=res_model, res_id=res_id,
            user_signature=user_signature)
        partner_ids = self.env.context.get('partners_to_notify')
        if footer and partner_ids:
            partners = self.env['res.partner'].browse(partner_ids)
            partners_name = [
                partner.name for partner in partners if
                partner.notify_email != 'none'
            ]
            additional_footer = u'<br /><small>%s%s</small><br />' %\
                (_('This message was also sent to: '),
                 ', '.join(partners_name))
            footer = tools.append_content_to_html(
                additional_footer, footer, plaintext=False,
                container_tag='div')

        return footer

    @api.one
    def _notify(
            self, partners_to_notify=None, force_send=False,
            user_signature=True):
        ctx = self.env.context.copy()
        if not self.env.context.get('mail_notify_noemail'):
            ctx.update({
                'partners_to_notify': partners_to_notify,
            })
        return super(MailNotification, self._model)._notify(
            self.env.cr, self.env.uid, self.id,
            partners_to_notify=partners_to_notify,
            force_send=force_send, user_signature=user_signature, context=ctx)
