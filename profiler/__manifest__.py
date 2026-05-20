# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Queue Job and Thread Profiler (Yappi)",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "yappi profiler decorator with database storage",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base"],
    "external_dependencies": {
        "python": ["yappi", "cairosvg", "flameprof"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/profiler_function_views.xml",
        "views/profiler_report_views.xml",
        "views/profiler_result_views.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
}
