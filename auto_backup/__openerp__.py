# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2015 Agile Business Group <http://www.agilebg.com>
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    "name": "Database Auto-Backup",
    "summary": "Backups database",
    "version": "9.0.1.1.1",
    "author": (
        "VanRoey.be - Yenthe Van Ginneken, Agile Business Group,"
        " Grupo ESOC Ingeniería de Servicios,"
        " Odoo Community Association (OCA)"
    ),
    'license': "AGPL-3",
    "website": "http://www.vanroey.be/applications/bedrijfsbeheer/odoo",
    "category": "Tools",
    "depends": ['mail'],
    "data": [
        "data/ir_cron.xml",
        "data/mail_message_subtype.xml",
        "security/ir.model.access.csv",
        "view/db_backup_view.xml",
    ],
    "application": True,
    "installable": True,
    "external_dependencies": {
        "python": ["pysftp"],
    },
}
