# coding: utf-8
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Repository of Modules',
    'version': '8.0.1.0.0',
    'summary': "Allows to see Repository Informations of Modules",
    'category': 'Tools',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/view_ir_module_module.xml',
        'views/view_ir_module_repository.xml',
    ],
    'images': [
        'static/src/img/screenshots/ir_module_repository_kanban.png',
        'static/src/img/screenshots/ir_module_module_kanban.png',
    ],
    'development_status': 'Beta',
    'external_dependencies': {
        'python': ['git'],
    },
}
