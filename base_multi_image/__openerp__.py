# -*- coding: utf-8 -*-
# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Multiple images base",
    "summary": "Allow multiple images for database objects",
    "version": "9.0.1.1.0",
    "author": "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Antiun Ingeniería, S.L., Sodexis, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "http://www.antiun.com",
    "category": "Tools",
    "depends": ['base'],
    'installable': False,
    "data": [
        "security/ir.model.access.csv",
        "views/image_view.xml",
    ],
    "images": [
        "images/form.png",
        "images/kanban.png",
    ],
}
