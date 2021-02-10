# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo import models


class IrExport(models.Model):
    """Because of jsonify.stored.mixin, models might depend on ir.exports records.
       These records are identifiable by xmlid.
       Therefore, when modifying a record we need to check that no models depend
       on it, or update the corresponding model.
    """

    _inherit = "ir.exports"

    def write(self, vals):
        if "export_fields" in vals:
            self._check_jsonify_stored()
        res = super(IrExport, self).write(vals)
        return res

    def _check_jsonify_stored(self):
        # if "jsonify.stored.mixin" not in self.env:
        #     return  # might be necessary in some weird cases?
        xml_ids = self.get_xml_id().values()
        jsonify_mixin = self.env["jsonify.stored.mixin"]
        jsonified_models = [self.env[m] for m in jsonify_mixin._inherit_children]
        models = [m for m in jsonified_models if m._get_export_xmlid() in xml_ids]
        for model in models:
            recompute_field = model._fields["jsonify_date_update"]
            recompute_field.depends = model._jsonify_get_export_depends()
            self.pool.setup_models(self._cr)
            self.pool.init_models(self._cr, [model._name], {})
            domain = [("jsonify_data_todo", "=", False)]
            model.search(domain).write({"jsonify_date_update": time.time()})
