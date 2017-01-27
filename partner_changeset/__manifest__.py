# -*- coding: utf-8 -*-
# Copyright 2015-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': 'Partner Changesets',
 'version': '10.0.1.0.0',
 'author': 'Camptocamp, Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Sales Management',
 'depends': ['base',
             'sale',
             ],
 'website': 'http://www.camptocamp.com',
 'data': ['security/security.xml',
          'security/ir.model.access.csv',
          'views/menu.xml',
          'views/res_partner_changeset_views.xml',
          'views/changeset_field_rule_views.xml',
          'views/res_partner_views.xml',
          ],
 'demo': ['demo/changeset_field_rule.xml',
          ],
 'installable': True,
 }
