# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class BaseImportImport(models.TransientModel):

    _inherit = 'base_import.import'

    @api.multi
    def do(self, fields, options, dryrun=False):
        self.ensure_one()
        if options.get('defer_parent_store_computation'):
            self = self.with_context(defer_parent_store_computation=True)
        return super(BaseImportImport, self).do(fields, options, dryrun=dryrun)
