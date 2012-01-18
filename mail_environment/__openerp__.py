# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright Camptocamp SA
##############################################################################
{
    'name': 'Server env config for mail + fetchmail',
    'version': '0.1',
    'category': 'Tools',
    'description': """
Extend mail and fetch mail with server environment module.

In config files, sections outgoint_mail and incoming_mails are default values for all Outgoing Mail Servers and Fetchmail Servers.
For each server, you can (re)define values with a section named "outgoing_mail.resource_name" where resource_name is the name of your server.

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
    'author': 'Camptocamp',
    'website': 'http://openerp.camptocamp.com',
    'depends': ['mail', 'fetchmail', 'server_environment', 'server_environment_files', 'crm'],
    'init_xml': [],
    'update_xml': ['mail_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
