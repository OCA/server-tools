# Copyright 2015 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2017 Eficent <http://www.eficent.com>
# Copyright 2018 Hai Dinh <haidd.uit@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Fetchmail Notify Error to Sender',
    'summary': 'If fetching mails gives error, send an email to sender',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'author':
        "Agile Business Group,Eficent,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/server-tools',
    'license': 'AGPL-3',
    'depends': [
        'fetchmail',
        'test_mail',
    ],
    'data': [
        'views/fetchmail_view.xml',
        'data/email_template_data.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
}
