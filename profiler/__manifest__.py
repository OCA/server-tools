{
    'name': "profiler",
    'author': "Vauxoo, Therp BV, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/server-tools",
    'category': 'Tests',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': ["document"],
    'data': [
        'security/ir.model.access.csv',
        'views/profiler_profile_view.xml',
    ],
    'post_load': 'post_load',
    'installable': True,
    'maintainers': ['thomaspaulb']
}
