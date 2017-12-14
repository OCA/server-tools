# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import AccessError


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.multi
    def export_data(self, fields_to_export, raw_data=False):
        if self.env.user.has_group('base_export_security.export_group'):
            field_names = map(
                lambda path_array: path_array[0], map(
                    models.fix_import_export_id_paths,
                    fields_to_export,
                ),
            )
            self.env['export.event'].log_export(self, field_names)
            return super(Base, self).export_data(fields_to_export, raw_data)
        else:
            raise AccessError(
                _('You do not have permission to export data'),
            )
