# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> Daniel Reis <dreis.pt@hotmail.com>
# Copyright <YEAR(S)> Glen Dromgoole <gdromgoole@tier1engineering.com>
# Copyright <YEAR(S)> Loic Lacroix <loic.lacroix@savoirfairelinux.com>
# Copyright <YEAR(S)> Sandy Carter <sandy.carter@savoirfairelinux.com>
# Copyright <YEAR(S)>Gervais Naoussi <gervaisnaoussi@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Key Performance Indicator",
    "version": "9.0.1.0.0",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    "license": "AGPL-3",
    "category": "Report",
    "complexity": "normal",
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
