# Copyright 2012 - Now Savoir-faire Linux <https://www.savoirfairelinux.com/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Key Performance Indicator",
    "version": "12.0.1.1.0",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    "license": "AGPL-3",
    "category": "Report",
    "depends": [
        'base_external_dbsource',
        'web_widget_color',
    ],
    "data": [
        'security/kpi_security.xml',
        'security/ir.model.access.csv',
        'views/kpi_category_views.xml',
        'views/kpi_history_views.xml',
        'views/kpi_threshold_range_views.xml',
        'views/kpi_threshold_views.xml',
        'views/kpi_views.xml',
        'views/menu.xml',
        'data/kpi_data.xml',
    ],
    "images": [
        "images/kpi_definition.png",
        "images/kpi_computation.png",
        "images/kpi_threshold.png",
        "images/kpi_range.png",
    ],
    'installable': True,
}
