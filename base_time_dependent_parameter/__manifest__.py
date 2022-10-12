# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Time Dependent Parameter",
    "version": "14.0.1.0.1",
    "summary": """
        Time dependent parameters
        Adds the feature to define parameters
        with time based versions.
    """,
    "license": "AGPL-3",
    "author": "Nimarosa, Odoo Community Association (OCA)",
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
    ],
    "installable": True,
}
