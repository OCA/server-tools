# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2016 Grupo ESOC Ingenieria de Servicios, S.L.U. - Jairo Llopis
# Copyright 2019 Numigi (tm) and its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Database Auto-Backup",
    "summary": "Backups database",
    "version": "12.0.1.1.1",
    "author":
        "Yenthe Van Ginneken, "
        "Agile Business Group, "
        "Grupo ESOC Ingenieria de Servicios, "
        "LasLabs, "
        "AdaptiveCity, "
        "Numigi, "
        "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools/",
    "category": "Tools",
    "depends": [
        "mail",
    ],
    "data": [
        "data/ir_cron.xml",
        "data/mail_message_subtype.xml",
        "security/ir.model.access.csv",
        "view/db_backup_view.xml",
    ],
    "installable": True,
    "external_dependencies": {
        "python": ["pysftp"],
    },
}
