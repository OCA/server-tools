# Copyright  2012-2015 Agile Business Group sagl (<http://www.agilebg.com>)
#                      Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright  2012      Domsense srl (<http://www.domsense.com>)
# Copyright  2015      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Alejandro Santana <alejandrosantana@anubia.es>
# Copyright  2015      Savoir-faire Linux <http://www.savoirfairelinux.com>)
#                      Agathe Mollé <agathe.molle@savoirfairelinux.com>

# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Super Calendar',
    'version': '12.0.1.0.0',
    'category': 'Generic Modules/Others',
    'summary': 'This module allows to create configurable calendars.',
    'author': ('Agile Business Group, '
               'Alejandro Santana, '
               'Agathe Mollé, '
               'Odoo Community Association (OCA)'),
    'website': 'https://github.com/OCA/server-tools',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'views/super_calendar_view.xml',
        'data/cron_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
