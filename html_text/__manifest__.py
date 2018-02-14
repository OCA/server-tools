# Copyright 2016-2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Text from HTML field",
    "summary": "Generate excerpts from any HTML field",
    "version": "11.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Grupo ESOC Ingeniería de Servicios, "
              "Tecnativa, "
              "Onestein, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [
            "lxml.html",
        ],
    },
    "depends": [
        "base",
    ],
}
