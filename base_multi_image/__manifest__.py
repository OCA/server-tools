# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# © 2016 Sodexis
# © 2024 Omal bastin <omalbastin@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Multiple images base",
    "summary": "Allow multiple images for database objects",
    "version": "17.0.1.0.0",
    "author": "Tecnativa, "
    "Antiun Ingeniería, S.L., Sodexis, "
    "LasLabs, "
    "Omal Bastin (O4ODOO), "
    "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["base"],
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "views/image_view.xml",
    ],
    "images": [
        "images/form.png",
        "images/kanban.png",
    ],
}
