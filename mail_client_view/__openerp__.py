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

{
    'name': 'User email access',
    'version': '6.1.r0025',
    'description': '''
    Adds a menu to the customer address book that enables ordinary users to
    look at customer or other mail. Also adds an 'action needed' boolean to
    mail messages, to quickly select all mails that still have to be acted on.
    
    The action_needed flag will be shown to users in a tree view as a red
    circle, no action needed will be green. In a form users either have the
    button 'confirm action done' (if action needed), or the button 'set
    action needed.
    ''',
    'author': 'Therp BV',
    'website': 'http://www.therp.nl',
    'category': 'Tools',
    'depends': ['mail'],
    'data': [
        'view/mail_user_menu.xml',
        'view/mail_user_view.xml',
        ],
    'js': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
