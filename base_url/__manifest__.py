#    Rewrite url Base module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Url",
    "version": "18.0.1.0.0",
    "category": "tools",
    "license": "AGPL-3",
    "summary": "Abstract module/mixin to manage clean url on odoo record",
    "author": "Akretion, ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base", "base_sparse_field_list_support"],
    "maintainers": ["sebastienbeau"],
    "external_dependencies": {"python": ["python-slugify"]},
    "data": [
        "views/url_view.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
