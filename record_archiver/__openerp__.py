# -*- coding: utf-8 -*-
# © 2015 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{'name': 'Records Archiver',
 'version': '9.0.1.0.0',
 'author': 'Camptocamp,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'misc',
 'depends': ['base'],
 'website': 'www.camptocamp.com',
 'data': ['views/record_lifespan_view.xml',
          'data/cron.xml',
          'security/ir.model.access.csv',
          ],
 'installable': True,
 'auto_install': False,
 }
