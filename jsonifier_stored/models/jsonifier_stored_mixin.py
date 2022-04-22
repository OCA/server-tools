# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# @author Matthieu Méquignon <matthieu.mequignon@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json
import logging
from collections import namedtuple
from itertools import groupby

from odoo import api, fields, models
from odoo.tools.misc import get_lang, split_every

from odoo.addons.base_sparse_field.models.fields import Serialized

GrouperAndSorter = namedtuple("GrouperAndSorter", "exporter_id lang")

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
            lang_code = (grouper.lang or default_lang).code
            # `get_json_parser` is cached
            parser = exporter.get_json_parser()
            self._update_jsonified_data(records.with_context(lang=lang_code), parser)

    def _compute_jsonified_data_groupby(self):
        _grouper_and_sorter = self._jsonify_data_grouper_and_sorter
        return groupby(self.sorted(_grouper_and_sorter), key=_grouper_and_sorter)

    def _get_default_lang(self):
        return get_lang(self.env)

    @property
    def _jsonify_lang_field_name(self):
        """Field providing specific language per record."""
        return "lang_id"

    @property
    def _jsonify_lang_field_exists(self):
        return self._jsonify_lang_field_name in self._fields

    @staticmethod
    def _jsonify_data_grouper_and_sorter(rec):
        lang = None
        if rec._jsonify_lang_field_exists:
            # Support translated records.
            lang = rec[rec._jsonify_lang_field_name]
        return GrouperAndSorter(rec.ir_export_id, lang)

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
        lang_domains=None,
        job_params=None,
    ):
        """Generate jobs to compute JSON data for given model.

        If the curent model has a `lang_id` field, one job-ification per lang will be triggered.
        """
        _logger.info("cron_update_json_data_for: %s", model_name)
        model = self.env[model_name]
        domain = domain or []
        lang_domains = lang_domains or []
        if model._jsonify_lang_field_exists and not lang_domains:
            lang_domains = model._json_data_compute_get_lang_domains()
        for lang_domain in lang_domains:
            lang_code = lang_domain[0][-1]
            if isinstance(lang_code, int):
                # got an ID
                lang_code = self.env["res.lang"].browse(lang_code).code
            self.jobify_json_data_compute_for(
                model,
                chunk_size=chunk_size,
                domain=domain + lang_domain,
                lang=lang_code,
                job_params=job_params,
            )
        if not lang_domains:
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
        return self.env.ref(
            "jsonifier_stored.channel_jsonifier_stored_root"
        ).complete_name

    @api.model
    def _json_data_compute_get_lang_domains(self):
        """Retrieve all domain leaves by language."""
        # Using read_group we support in the same way lang fields as m2o and string
        # as well as fields coming from models inherited w/ `inherits`.
        # For instance:
        # >>> env["res.partner"].read_group([], ["id"], ["lang"])
        # [{'lang_count': 620, 'lang': 'de_DE', '__domain': [('lang', '=', 'de_DE')]},
        #  {'lang_count': 3, 'lang': 'en_US', '__domain': [('lang', '=', 'en_US')]}]
        # >>> env["model.with.m2o"].read_group([], ["id"], ["lang_id"])
        # [{'lang_id_count': 1579,
        # 'lang_id': (30, <odoo.tools.func.lazy object at 0x7f2a976a4798>),
        # '__domain': [('lang_id', '=', 30)]}]
        by_lang = self.read_group([], ["id"], [self._jsonify_lang_field_name])
        return [x["__domain"] for x in by_lang]
