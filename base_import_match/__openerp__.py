# -*- coding: utf-8 -*-
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Base Import Match",
    "summary": "Try to avoid duplicates before importing",
    "version": "8.0.1.0.0",
    "category": "Tools",
    "website": "https://grupoesoc.es",
    "author": "Grupo ESOC Ingeniería de Servicios, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base_import",
    ],
    "data": [
        "views/base_import_match_view.xml",
    ],
    "demo": [
        "demo/base_import_match.yml",
    ],
}
