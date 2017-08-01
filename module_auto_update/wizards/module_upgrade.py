# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, models


class ModuleUpgrade(models.TransientModel):
    _inherit = 'base.module.upgrade'

    @api.multi
    def upgrade_module_cancel(self):
        return super(
            ModuleUpgrade,
            self.with_context(retain_checksum_installed=True),
        ).upgrade_module_cancel()

    @api.multi
    def upgrade_module(self):
        self.env['ir.module.module'].update_list()
        return super(ModuleUpgrade, self).upgrade_module()
