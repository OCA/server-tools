# -*- coding: utf-8 -*-
# Copyright 2017-2019 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IrFilesystemDirectory(models.Model):
    _inherit = 'ir.filesystem.directory'

    is_backup = fields.Boolean()

    @api.multi
    def get_dir(self):
        if self.is_backup:
            backup = self.env['db.backup'].search([], limit=1)
            if not backup:
                raise UserError(_(
                    'No backup configuration.'))
            self.directory = backup.folder
        return super(IrFilesystemDirectory, self).get_dir()
