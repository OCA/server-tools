# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Mail message name search",
    "version": "8.0.1.0.0",
    "author": "Eficent,"
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "CRM",
    "data": ["data/trgm_index_data.xml"],
    "depends": ["mail",
                "base_search_fuzzy"],
    "license": "AGPL-3",
    'installable': True,
}
