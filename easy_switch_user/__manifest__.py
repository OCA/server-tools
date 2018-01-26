{
    'name': 'Easy Switch User',
    'summary': 'Lets administrators and developers quickly '
               'change user to test e.g. access rights',
    'category': 'Tools',
    'version': '11.0.1.0.0',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'license': 'AGPL-3',
    'depends': [
        'web'
    ],
    'qweb': [
        'static/src/xml/switch_user.xml'
    ],
    'data': [
        'templates/assets.xml'
    ],
    'installable': True,
    'application': False,
}
