#    Rewrite url Base module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Url",
    "version": "16.0.1.0.2",
    "category": "tools",
    "license": "AGPL-3",
    "summary": "keep history of url for products & categories  ",
    "author": "Akretion, ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    # any module necessary for this one to work correctly
    "depends": ["base"],
    "external_dependencies": {"python": ["python-slugify"]},
    "data": ["views/url_view.xml", "security/ir.model.access.csv"],
    "url": "",
    "installable": True,
}
