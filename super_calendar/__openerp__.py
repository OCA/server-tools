# -*- coding: utf-8 -*-
# Copyright
#        (c) 2012-2015 Agile Business Group sagl (<http://www.agilebg.com>)
#                      Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#        (c) 2012      Domsense srl (<http://www.domsense.com>)
#        (c) 2015      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Alejandro Santana <alejandrosantana@anubia.es>
#        (c) 2015      Savoir-faire Linux <http://www.savoirfairelinux.com>)
#                      Agathe Mollé <agathe.molle@savoirfairelinux.com>
#        (c) 2016      Serpent Consulting Services Pvt. Ltd.
#                      (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Super Calendar',
    'version': '9.0.1.0.0',
    'category': 'Generic Modules/Others',
    'summary': 'This module allows to create configurable calendars.',
    'author': ('Agile Business Group, '
               'Alejandro Santana, '
               'Agathe Mollé, '
               'Odoo Community Association (OCA), '
               'Serpent Consulting Services Pvt. Ltd.'),
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
    'installable': True,
    'demo': [],
    'test': [],
#     'installable': True,
    'application': True,
    'auto_install': False,
}
