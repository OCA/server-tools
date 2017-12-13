# -*- coding: utf-8 -*-
# Copyright 2012 - Now Savoir-faire Linux <https://www.savoirfairelinux.com/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Key Performance Indicator",
    "version": "9.0.1.1.0",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    "license": "AGPL-3",
    "category": "Report",
    "depends": [
        'base_external_dbsource',
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/kpi_security.xml',
        'views/kpi_category.xml',
        'views/kpi_history.xml',
        'views/kpi_threshold_range.xml',
        'views/kpi_threshold.xml',
        'views/kpi.xml',
        'views/menu.xml',
        'data/kpi.xml',
    ],
    "images": [
        "images/kpi_definition.png",
        "images/kpi_computation.png",
        "images/kpi_threshold.png",
        "images/kpi_range.png",
    ],
    'installable': True,
}
