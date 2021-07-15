# -*- coding: utf-8 -*-
# Copyright 2015 Anubía, soluciones en la nube,SL (http://www.anubia.es)
# Copyright 2017 Onestein (http://www.onestein.eu)
# Copyright 2021 ArcheTI (http://www.archeti.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Optional CSV import',
    'version': '12.0.1.0.0',
    'category': 'Server tools',
    'summary': 'Group-based permissions for importing CSV files',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA), '
              'Alejandro Santana <alejandrosantana@anubia.es>, '
              'Onestein, '
              'ArcheTI',
    'maintainer': 'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'depends': [
        'web',
        'base_import',
    ],
    'data': [
        'security/base_import_security_group_security.xml',
        'views/base_import.xml',
        'views/model_view.xml',
    ],
    'installable': True,
}
