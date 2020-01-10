# 2019  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'IrSequence Standard by Default',
    'summary': 'Use Standard implementation of ir.sequence instead of NoGap',
    'version': '12.0.1.0.0',
    'author': 'Vauxoo, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'maintainers': ['moylop260', 'ebirbe'],
    'license': 'AGPL-3',
    'category': 'Tools',
    'depends': [
        'base_setup',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'wizard/sequence_standard_default_views.xml',
    ],
    'installable': True,
    'application': False,
}
