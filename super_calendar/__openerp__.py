# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) All rights reserved:
#        (c) 2012-2015 Agile Business Group sagl (<http://www.agilebg.com>)
#                      Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#        (c) 2012      Domsense srl (<http://www.domsense.com>)
#        (c) 2015      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Alejandro Santana <alejandrosantana@anubia.es>
#        (c) 2015      Savoir-faire Linux <http://www.savoirfairelinux.com>)
#                      Agathe Mollé <agathe.molle@savoirfairelinux.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#
##############################################################################
{
    'name': 'Super Calendar',
    'version': '8.0.0.2.0',
    'category': 'Generic Modules/Others',
    'summary': 'This module allows to create configurable calendars.',
    'author': ('Agile Business Group, '
               'Alejandro Santana, '
               'Agathe Mollé, '
               'Odoo Community Association (OCA)'),
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web_calendar',
    ],
    'data': [
        'views/super_calendar_view.xml',
        'data/cron_data.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
