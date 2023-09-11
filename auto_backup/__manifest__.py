# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2016 Grupo ESOC Ingenieria de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Database Auto-Backup",
    "summary": "Backups database",
    "version": "16.0.1.0.0",
    "author": "Yenthe Van Ginneken, "
    "Agile Business Group, "
    "Grupo ESOC Ingenieria de Servicios, "
    "LasLabs, "
    "AdaptiveCity, "
    "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["mail"],
    "data": [
        "data/ir_cron.xml",
        "data/mail_message_subtype.xml",
        "security/ir.model.access.csv",
        "view/db_backup_view.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["pysftp", "cryptography"]},
}
