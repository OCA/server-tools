# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json
from itertools import groupby

from odoo import api, fields, models
from odoo.tools.misc import split_every


class JsonifyStoredMixin(models.AbstractModel):
    """This mixin aims to provide the ability to store jsonified data on model."""

    _name = "jsonify.stored.mixin"

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

    def _jsonify_get_exporter(self):
        """Hook to get the exporter to use."""
        return False

    def _compute_jsonified_display(self):
        for record in self:
            record.jsonified_display = json.dumps(
                record.jsonified_data, sort_keys=True, indent=4
            )

    def _chunk(self, size=1000):
        for chunk in split_every(size, self.ids):
            yield self.browse(chunk)

    @api.depends(
        "ir_export_id", "ir_export_id.export_fields", "ir_export_id.export_fields.name"
    )
    def _compute_jsonified_data(self):
        for export, group in self._group_by_export():
            records = self.browse([r.id for r in group])
            # TODO explain : shouldn't happen
            if not export:
                records.jsonified_data = False
                continue
            parser = export.get_json_parser()
            jsonified_data = self._get_jsonified_data(parser)
            for record, data in zip(records, jsonified_data):
                record.jsonified_data = data

    def _group_by_export(self):
        self = self.sorted("ir_export_id")
        return groupby(self, key=lambda r: r.ir_export_id)

    def _get_jsonified_data(self, parser):
        return self.jsonify(parser)

    @api.model
    def cron_update_jsonify_stored(self):
        # As there could be a lot of records, chunk the recordset before
        # computing the jsonified data
        records = self.search([])
        for chunk in records._chunk():
            chunk.with_delay()._compute_jsonified_data()
