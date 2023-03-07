# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Disable RPC",
    "summary": """Helpers for disabling RPC calls""",
    "version": "14.0.1.1.1",
    "development_status": "Alpha",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["simahawk"],
    "depends": ["base_sparse_field"],
    "data": ["views/ir_model_views.xml"],
    "post_load": "post_load_hook",
}
