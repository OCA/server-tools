# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# @author Matthieu Méquignon <matthieu.mequignon@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json
import logging
from collections import namedtuple
from itertools import groupby

from psycopg2.extensions import AsIs

from odoo import api, fields, models
from odoo.tools.misc import get_lang, split_every

from odoo.addons.base_sparse_field.models.fields import Serialized

GrouperAndSorter = namedtuple("GrouperAndSorter", "exporter_id lang_code")

_logger = logging.getLogger(__file__)


class JsonifyStoredMixin(models.AbstractModel):
    """This mixin aims to provide the ability to store jsonified data on model."""

    _name = "jsonifier.stored.mixin"
    _description = "JSONifier stored mixin"

    # TODO: writeable, stored, compute default value, filter by current model?
    ir_export_id = fields.Many2one("ir.exports", compute="_compute_ir_export_id")
    jsonified_display = fields.Text(
        compute="_compute_jsonified_display",
    )
    jsonified_data = Serialized(compute="_compute_jsonified_data", store=True)

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

    def _compute_jsonified_data(self):
        """Compute JSON data for current recordset.

        Optimized to always group by lang and parser
        even when large mixed recordsets are updated.
        """
        default_lang = self._get_default_lang()
        for grouper, group in self._compute_jsonified_data_groupby():
            records = self.browse([r.id for r in group])
            exporter = grouper.exporter_id
            if not exporter:
                records.jsonified_data = False
                _logger.error("%s have no exporter", str(records._name))
                continue
            lang_code = grouper.lang_code or default_lang
            # `get_json_parser` is cached
            parser = exporter.get_json_parser()
            self._update_jsonified_data(records.with_context(lang=lang_code), parser)

    def _compute_jsonified_data_groupby(self):
        _grouper_and_sorter = self._jsonify_data_grouper_and_sorter
        return groupby(self.sorted(_grouper_and_sorter), key=_grouper_and_sorter)

    def _get_default_lang(self):
        return get_lang(self.env)

    @staticmethod
    def _jsonify_data_grouper_and_sorter(rec):
        lang_code = None
        if "lang_id" in rec._fields:
            # Support translated records.
            lang_code = rec.lang_id.code
        return GrouperAndSorter(rec.ir_export_id, lang_code)

    def _update_jsonified_data(self, records, parser):
        json_vals = records._get_jsonified_data(parser)
        for record, data in zip(records, json_vals):
            record.jsonified_data = data

    def _get_jsonified_data(self, parser):
        # Hook to override data
        return self.jsonify(parser)

    @api.model
    def cron_update_json_data_for(
        self,
        model_name,
        chunk_size=5,
        domain=None,
        langs=None,
        job_params=None,
    ):
        """Generate jobs to compute JSON data for given model.

        If the curent model has a `lang_id` field, one job-ification per lang will be triggered.
        """
        _logger.info("cron_update_json_data_for: %s", model_name)
        model = self.env[model_name]
        domain = domain or []
        if "lang_id" in model._fields and not langs:
            langs = model._json_data_compute_get_all_langs()
        if langs:
            for lang in langs:
                self.jobify_json_data_compute_for(
                    model,
                    chunk_size=chunk_size,
                    domain=domain + [("lang_id.code", "=", lang)],
                    lang=lang,
                    job_params=job_params,
                )
        else:
            self.jobify_json_data_compute_for(
                model,
                chunk_size=chunk_size,
                domain=domain,
                job_params=job_params,
            )

    @api.model
    def jobify_json_data_compute_for(
        self, model, chunk_size=5, domain=None, ids=None, lang=None, job_params=None
    ):
        ids = ids or model.search(domain or []).ids
        job_params = model._jobify_json_data_compute_job_params(
            lang=lang, **job_params or {}
        )
        for ids_chunk in split_every(chunk_size, ids):
            self.with_delay(**job_params).jsonify_compute_data_for(
                model._name, ids_chunk
            )

    @api.model
    def jsonify_compute_data_for(self, model_name, ids):
        self.env[model_name].browse(ids)._compute_jsonified_data()

    @api.model
    def _jobify_json_data_compute_job_params(self, lang=None, **params):
        desc = params.get("description", "").strip()
        if not desc:
            desc = f"Compute JSON data for: {self._name}"
        if lang:
            desc += f" ({lang})"
        channel = params.get(
            "channel", self._jobify_json_data_compute_default_channel()
        )
        params.update(
            {
                "channel": channel,
                "description": desc,
            }
        )
        return params

    @api.model
    def _jobify_json_data_compute_default_channel(self):
        return self.env.ref("jsonify_stored.channel_jsonify_stored_root").complete_name

    @api.model
    def _json_data_compute_get_all_langs(self, table=None):
        # Some models might get tha lang_id fields from an inherits model.
        # If that's the case, allow to override this to pass the right table.
        table = table or self._table
        # get them all
        query = """
        SELECT DISTINCT lang.code
        FROM %s model, res_lang lang
        WHERE model.lang_id = lang.id
        """
        self.env.cr.execute(query, (AsIs(table),))
        return [x[0] for x in self.env.cr.fetchall()]
