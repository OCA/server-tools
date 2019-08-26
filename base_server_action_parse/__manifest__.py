{
    'name': 'Base Server Action Parse',
    'summary': 'Allows you to parse the base64 files at ir.actions.server',
    'version': '12.0.0.0.1',
    'category': 'Tools',
    'author': 'Vauxoo, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
    ],
    'external_dependencies': {
        'python': [
            'lxml',
        ]
    },
    'installable': True,
    'auto_install': False,
}
