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
        extend mail and fetch mail with server env
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
