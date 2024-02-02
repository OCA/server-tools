# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright Camptocamp SA
##############################################################################
{'name': 'Security protector',
 'version': '0.1',
 'category': 'Tools',
 'description': """
    Prevent security to be changed when module is updated
    This module overwrite ir model acces write delete function.
    Only acces edited trough the UI or with manual_security_override in context set to True will be altered.
    When you try to delete a acces write it simply set all perms to false
    you can deactivate this behavior in ir.config_parameter by chanching the protect_security? key to 0
 """,
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'website': 'https://github.com/OCA/server-tools',
 'license': 'AGPL-3',
 'depends': ['base'],
 'init_xml': ['data.xml'],
 'update_xml': ['security_view.xml'],
 'demo_xml': [],
 'installable': False,
 'auto_install': False,
 }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
