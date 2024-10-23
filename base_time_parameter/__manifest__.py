# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Time Parameter",
    "version": "16.0.1.0.0",
    "summary": """
        Time dependent parameters
        Adds the feature to define parameters
        with time based versions.
    """,
    "license": "LGPL-3",
    "author": "Nimarosa, appstogrow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "maintainers": ["appstogrow", "nimarosa"],
    "category": "Technical",
    "depends": [
        "base",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/base_time_parameter_views.xml",
        "views/base_time_parameter_version_views.xml",
    ],
    "development_status": "Beta",
    "installable": True,
}
