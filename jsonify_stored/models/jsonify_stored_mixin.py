# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json
from itertools import groupby

from odoo import api, fields, models, tools
from odoo.tools.misc import split_every


class JsonifyStoredMixin(models.AbstractModel):
    """This mixin aims to provide the ability to store jsonified data on model."""

    _name = "jsonify.stored.mixin"
    _description = __doc__

    def _ir_export_id_domain(self):
        return [("resource", "=", self._name)]

    # TODO writeable, compute default value, fitler by current model
    ir_export_id = fields.Many2one("ir.exports", compute="_compute_ir_export_id")
    jsonified_display = fields.Text(
        compute="_compute_jsonified_display",
    )
    jsonified_data = fields.Serialized(compute="_compute_jsonified_data", store=True)

    def _compute_ir_export_id(self):
        for record in self:
            record.ir_export_id = record._jsonify_get_exporter()

    def _jsonify_get_exporter_cache_keys(self):
        return ("self._name",)

    @tools.ormcache("self._jsonify_get_exporter_cache_keys()")
    def _jsonify_get_exporter(self):
        """Hook to get the exporter to use."""
        return False

    def _compute_jsonified_display(self):
        for record in self:
            record.jsonified_display = json.dumps(
                record.jsonified_data, sort_keys=True, indent=4
            )

    def _compute_jsonified_data(self):
        for export, group in self._compute_jsonified_data_groupby():
            records = self.browse([r.id for r in group])
            # TODO explain : shouldn't happen
            if not export:
                records.jsonified_data = False
                continue
            parser = export.get_json_parser()
            jsonified_data = self._get_jsonified_data(parser)
            for record, data in zip(records, jsonified_data):
                record.jsonified_data = data

    def _compute_jsonified_data_groupby(self):
        return groupby(self.sorted("ir_export_id"), key=lambda r: r.ir_export_id)

    def _get_jsonified_data(self, parser):
        return self.jsonify(parser)

    @api.model
    def cron_update_jsonify_stored(self, chunk_size=10, domain=None):
        # As there could be a lot of records, chunk the recordset before
        # computing the jsonified data
        ids = self.search(domain or []).ids
        for ids_chunk in split_every(chunk_size, ids):
            self.browse(ids_chunk).jobify_compute_jsonified_data()

    def jobify_compute_jsonified_data(self):
        self.with_delay()._compute_jsonified_data()
