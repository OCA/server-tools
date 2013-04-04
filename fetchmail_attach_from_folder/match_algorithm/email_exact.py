# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from base import base
from openerp.tools.safe_eval import safe_eval
from openerp.addons.mail.mail_message import to_email

class email_exact(base):
    '''Search for exactly the mailadress as noted in the email'''

    name = 'Exact mailadress'
    required_fields = ['model_field', 'mail_field']

    def _get_mailaddresses(self, conf, mail_message):
        mailaddresses = []
        fields = conf.mail_field.split(',')
        for field in fields:
            if field in mail_message:
                mailaddresses += to_email(mail_message[field])
        return [ addr.lower() for addr in mailaddresses ]

    def _get_mailaddress_search_domain(
            self, conf, mail_message, operator='=', values=None):
        mailaddresses = values or self._get_mailaddresses(
                conf, mail_message)
        if not mailaddresses:
            return [(0, '=', 1)]
        search_domain = ((['|'] * (len(mailaddresses) - 1)) + [
                (conf.model_field, operator, addr) for addr in mailaddresses] +
                safe_eval(conf.domain or '[]'))
        return search_domain

    def search_matches(self, cr, uid, conf, mail_message, mail_message_org):
        conf_model = conf.pool.get(conf.model_id.model)
        search_domain = self._get_mailaddress_search_domain(conf, mail_message)
        return conf_model.search(
            cr, uid, search_domain, order=conf.model_order)
