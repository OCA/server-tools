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

class base(object):
    name = None
    '''Name shown to the user'''

    required_fields = []
    '''Fields on fetchmail_server folder that are required for this algorithm'''

    readonly_fields = []
    '''Fields on fetchmail_server folder that are readonly for this algorithm'''


    def search_matches(self, cr, uid, conf, mail_message, mail_message_org):
        '''Returns ids found for model with mail_message'''
        return []

    def handle_match(
            self, cr, uid, connection, object_id, folder,
            mail_message, mail_message_org, msgid, context=None):
        '''Do whatever it takes to handle a match'''
        return folder.server_id.attach_mail(connection, object_id, folder,
                mail_message, msgid)
