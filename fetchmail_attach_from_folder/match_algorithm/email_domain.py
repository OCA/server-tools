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

from email_exact import email_exact

class email_domain(email_exact):
    '''Search objects by domain name of email address.
    Beware of match_first here, this is most likely to ge it wrong (gmail...)'''
    name = 'Domain of email address'

    def search_matches(self, cr, uid, conf, mail_message, mail_message_org):
        ids = super(email_domain, self).search_matches(
                cr, uid, conf, mail_message, mail_message_org)
        if not ids:
            domains = []
            for addr in self._get_mailaddresses(conf, mail_message):
                domains.append(addr.split('@')[-1])
            ids = conf.pool.get(conf.model_id.model).search(
                    cr, uid,
                    self._get_mailaddress_search_domain(
                        conf, mail_message,
                        operator='like',
                        values=['%@'+domain for domain in set(domains)]),
                    order=conf.model_order)
        return ids
