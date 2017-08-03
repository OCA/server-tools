# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    installed_modules = env['ir.module.module'].search([
        ('state', '=', 'installed'),
    ])
    for r in installed_modules:
        r.checksum_installed = r.checksum_dir
