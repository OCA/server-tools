# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2015 Agile Business Group <http://www.agilebg.com>
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    "name": "Database Auto-Backup",
    "summary": "Backups database",
    "version": "10.0.2.0.0",
    "author": (
        "Yenthe Van Ginneken, "
        "Agile Business Group, "
        "Grupo ESOC Ingeniería de Servicios, "
        "LasLabs, "
        "Odoo Community Association (OCA)"
    ),
    'license': "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": [
        'mail',
        'connector_sftp',
    ],
    "data": [
        "data/ir_cron.xml",
        "data/mail_message_subtype.xml",
        "security/ir.model.access.csv",
        "view/db_backup_view.xml",
    ],
    "application": True,
    "installable": True,
}
