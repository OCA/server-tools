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

class openerp_standard(base):
    '''No search at all. Use OpenERP's standard mechanism to attach mails to
    mail.thread objects. Note that this algorithm always matches.'''

    name = 'OpenERP standard'
    readonly_fields = ['model_field', 'mail_field', 'match_first', 'domain',
            'model_order', 'flag_nonmatching']

    def search_matches(self, cr, uid, conf, mail_message, mail_message_org):
        '''Always match. Duplicates will be fished out by message_id'''
        return [True]

    def handle_match(
            self, cr, uid, connection, object_id, folder,
            mail_message, mail_message_org, msgid, context):
        result = folder.pool.get('mail.thread').message_process(
                cr, uid, 
                folder.model_id.model, mail_message_org,
                save_original=folder.server_id.original,
                strip_attachments=(not folder.server_id.attach),
                context=context)

        if folder.delete_matching:
            connection.store(msgid, '+FLAGS', '\\DELETED')

        return result
