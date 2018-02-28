# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import SUPERUSER_ID, api


def migrate(cr, version):
    with api.Environment.manage():
        cr.execute("""
            UPDATE ir_config_parameter
            SET key='module_checksum_upgrade.checksum_excluded_extensions'
            WHERE key='module_auto_update.checksum_excluded_extensions'
        """)
        cr.execute("""
            SELECT name, checksum_installed FROM ir_module_module
            WHERE checksum_installed is not NULL
        """)
        checksums = dict(cr.fetchall())
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['ir.module.module']._save_checksums(checksums)
