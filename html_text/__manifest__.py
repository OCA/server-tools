# -*- coding: utf-8 -*-
# Copyright 2016-2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Text from HTML field",
    "summary": "Generate excerpts from any HTML field",
    "version": "10.0.1.0.1",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools"
               "/tree/10.0/html_text",
    "author": "Grupo ESOC Ingeniería de Servicios, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [
            "lxml",
        ],
    },
    "depends": [
        "base",
    ],
}
