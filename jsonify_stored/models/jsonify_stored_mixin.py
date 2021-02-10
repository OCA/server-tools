# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo import api, fields, models


class JsonifyStored(models.AbstractModel):
    """Stores the data to export.
       When inheriting this class, _export_xmlid should be set with an export xml_id.
       Note that this xml_id has to exist before the model init,
       i.e. either be in a dependency module, or created in a pre_init_hook
       (however it's fine to modify an existing one in the module data).
    """

    _name = "jsonify.stored.mixin"
    _description = "Stores json data"

    _export_xmlid_pattern = "jsonify_export_{}"

    jsonify_data = fields.Serialized(
        string="Jsonify: Data",
        compute="_compute_jsonify_data",
        readonly=True,
        store=False,
        help="Json export value. Always up-to-date, triggers a recompute if necessary.",
    )
    jsonify_date_update = fields.Float(
        string="Last Record Update",
        compute="_compute_jsonify_date_update",
        readonly=True,
        store=True,
        help="Timestamp of the last time the Json needed to be recomputed.",
    )
    jsonify_date_compute = fields.Float(
        string="Last Json Update",
        compute="_compute_jsonify_date_compute",
        readonly=True,
        store=True,
        help="Timestamp of the last time the Json was computed.",
    )
    jsonify_data_todo = fields.Boolean(
        string="Jsonify: Todo",
        compute="_compute_jsonify_data_todo",
        default=True,
        readonly=True,
        store=True,
        help="If True, the stored json data needs to be recomputed.",
    )
    jsonify_data_stored = fields.Serialized(
        string="Jsonify: Stored",
        compute="_compute_jsonify_data_stored",
        readonly=True,
        store=True,
        help="Last computed Json export value. Might not be up to date.",
    )

    @api.model
    def _get_export_xmlid(self):
        return self._module + "." + self._export_xmlid_pattern.format(self._table)

    @api.model
    def _jsonify_get_export(self):
        export = self.env.ref(self._get_export_xmlid(), raise_if_not_found=False)
        return export or self.__create_jsonify_export()

    @api.model
    def __create_jsonify_export(self):
        name = "{} Export".format(self._description)
        export = self.env["ir.exports"].create({"name": name})
        vals_data = {
            "module": self._module,
            "name": self._export_xmlid_pattern.format(self._table),
            "model": export._name,
            "res_id": export.id,
        }
        self.env["ir.model.data"].create(vals_data)
        return export

    @api.model
    def _jsonify_get_export_depends(self):
        export_field_names = self._jsonify_get_export().export_fields.mapped("name")
        return tuple(fn.replace("/", ".") for fn in export_field_names)

    @api.depends(lambda self: self._jsonify_get_export_depends())
    def _compute_jsonify_date_update(self):
        now = time.time()
        for record in self:
            record.jsonify_date_update = now

    @api.depends("jsonify_data_stored")
    def _compute_jsonify_date_compute(self):
        now = time.time()
        for record in self:
            record.jsonify_date_compute = now

    @api.depends("jsonify_date_update", "jsonify_date_compute")
    def _compute_jsonify_data_todo(self):
        for record in self:
            time_todo = record.jsonify_date_update
            time_done = record.jsonify_date_compute
            record.jsonify_data_todo = time_done <= time_todo

    def _compute_jsonify_data_stored(self):
        if self:
            parser = self._jsonify_get_export().get_json_parser()
            data_list = self.jsonify(parser)
            for record, data in zip(self, data_list):
                record.jsonify_data_stored = data

    @api.depends("jsonify_data_todo", "jsonify_data_stored")
    def _compute_jsonify_data(self):
        to_recompute = self.filtered("jsonify_data_todo")
        if to_recompute:  # cascades the changes from the recompute
            to_recompute.modified(["jsonify_data_stored"])
            to_recompute.recompute()  # before, otherwise we lose the cached values
            to_recompute._compute_jsonify_data_stored()
        for record in self:
            record.jsonify_data = record.jsonify_data_stored

    @api.model
    def cron_recompute(self, limit=None):
        records = self.search([("jsonify_data_todo", "=", True)], limit=limit)
        records._compute_jsonify_data_stored()

    @api.model_create_multi
    def create(self, vals_list):
        res = super(JsonifyStored, self).create(vals_list)
        res._compute_jsonify_date_update()
        return res
