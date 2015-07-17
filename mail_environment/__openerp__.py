# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2012 Camptocamp SA
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

{
    'name': 'Server env config for mail + fetchmail',
    'version': '0.1',
    'category': 'Tools',
    'description': """
Extend mail and fetch mail with server environment module.

In config files, sections outgoing_mail and incoming_mails are default values
for all Outgoing Mail Servers and Fetchmail Servers.
For each server, you can (re)define values with a section named
"outgoing_mail.resource_name" where resource_name is the name of your server.

Exemple of config file :

[outgoing_mail]
smtp_host = smtp.myserver.com
smtp_port = 587
smtp_user =
smtp_pass =
smtp_encryption = ssl

[outgoing_mail.openerp_smtp_server1]
smtp_user = openerp
smtp_pass = openerp

[incoming_mail.openerp_pop_mail1]
server = mail.myserver.com
port = 110
type = pop
is_ssl = 0
attach = 0
original = 0
user = openerp@myserver.com
password = openerp


    """,
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'http://openerp.camptocamp.com',
    'depends': ['mail',
                'fetchmail',
                'server_environment',
                'server_environment_files',
                ],
    'data': ['mail_view.xml'],
    'demo': [],
    'installable': True,
    'active': False,
}
