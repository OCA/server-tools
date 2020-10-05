# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrExportLine(models.Model):
    _inherit = "ir.exports.line"

    def write(self, vals):
        result = super(IrExportLine, self).write(vals)
        if any(field in vals for field in ["name", "alias"]):
            self.mapped("export_id")._check_jsonify_stored()
        return result

    @api.model
    def create(self, vals):
        result = super(IrExportLine, self).create(vals)
        self.mapped("export_id")._check_jsonify_stored()
        return result

    def unlink(self):
        exports = self.mapped("export_id")
        result = super(IrExportLine, self).unlink()
        exports._check_jsonify_stored()
        return result
