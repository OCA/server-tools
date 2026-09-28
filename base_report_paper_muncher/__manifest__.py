# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Report Engine: Paper Muncher",
    "summary": (
        "Paper Muncher PDF rendering engine for QWeb reports, "
        "replacing wkhtmltopdf when the binary is available"
    ),
    "version": "17.0.1.0.0",
    "development_status": "Beta",
    "category": "Hidden/Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Odoo Community Association (OCA)",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "data/ir_config_parameter_data.xml",
    ],
    "external_dependencies": {
        "python": ["h11"],
    },
    "license": "LGPL-3",
    "installable": True,
    "application": False,
}
