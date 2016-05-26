# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.addons.auditlog import migrate_from_audittrail


def migrate(cr, version):
    """if we migrate from an older version, it's a migration from audittrail"""
    migrate_from_audittrail(cr)
