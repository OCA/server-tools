{
    'name': 'Mail Template Language Specific Attachments',
    'summary': 'Set language specific attachments on mail templates.',
    'author': 'Onestein,Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/server-tools',
    'category': 'Localization',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'mail'
    ],
    'data': [
        'views/mail_template_view.xml',

        'security/ir.model.access.csv'
    ],
    'installable': True,
}
