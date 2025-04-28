# Copyright 2016 ForgeFlow S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Fuzzy Search",
    "summary": "Fuzzy search with the PostgreSQL trigram extension",
    "category": "Uncategorized",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/server-tools",
    "author": "bloopark systems GmbH & Co. KG, "
    "ForgeFlow, "
    "Serpent CS, "
    "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": ["views/trgm_index.xml", "security/ir.model.access.csv"],
    "demo": ["demo/res_partner_demo.xml", "demo/TrgmIndex_demo.xml"],
    "installable": True,
    "post_load": "post_load",
}
