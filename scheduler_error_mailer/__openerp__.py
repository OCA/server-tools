# -*- encoding: utf-8 -*-
##############################################################################
#
#    Scheduler Error Mailer module for OpenERP
#    Copyright (C) 2012-2013 Akretion (http://www.akretion.com/)
#    @author: Sébastien Beau <sebastien.beau@akretion.com>
#    @author David Beal <bealdavid@gmail.com>
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Scheduler Error Mailer',
    'summary': 'Send an e-mail when a scheduler fails',
    'version': '1.0',
    'category': 'Extra Tools',
    'license': 'AGPL-3',
    'description': """
Scheduler Error Mailer
======================

This module adds the possibility to send an e-mail when a scheduler raises an error.""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['email_template'],
    'data': [
        'ir_cron.xml',
        'ir_cron_email_tpl.xml',
    ],
    'demo': ['ir_cron_demo.xml'],
    'images': ['images/scheduler_error_mailer.jpg'],
    'installable': True,
    'active': False,
}
