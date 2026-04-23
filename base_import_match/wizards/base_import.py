# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0-or-later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class BaseImport(models.TransientModel):
    _inherit = "base_import.import"

    @api.model
    def _convert_import_data(self, fields, options):
        """Extend the standard conversion to inject resolved database IDs.

        After the normal parse step, active ``base_import.match``
        configurations for the current model are evaluated.  When at least
        one row gets a match the ``.id`` column is prepended to both the
        field list and every data row, causing ``load()`` to perform updates
        instead of inserts for matched records.

        If the import file already contains an ``id`` or ``.id`` column, or
        no active configuration exists for the model, the result of
        ``super()`` is returned unchanged.

        :returns: (data, import_fields) — same contract as the parent method
        :rtype: (list(list(str)), list(str))
        """
        data, import_fields = super()._convert_import_data(fields, options)

        if ".id" in import_fields or "id" in import_fields:
            _logger.debug(
                "base_import_match: ID column already present for model %s;"
                " skipping automatic field matching.",
                self.res_model,
            )
            return data, import_fields

        match_configs = self.env["base_import.match"].search(
            [("model_name", "=", self.res_model)]
        )
        if not match_configs:
            return data, import_fields

        data, import_fields = self._apply_field_matching(
            data, import_fields, match_configs
        )
        return data, import_fields

    # ------------------------------------------------------------------
    # Matching helpers
    # ------------------------------------------------------------------

    def _apply_field_matching(self, data, import_fields, match_configs):
        """Iterate over every import row and inject the resolved database ID.

        For each row:
        * Unique match found   → prepend its database ID (update).
        * No match found       → prepend empty string (create).
        * Multiple matches     → skip row entirely (no create, no update).

        Returns the original objects unchanged when **no** row matched or
        was skipped, avoiding an unnecessary ``.id`` column in the load call.

        :param data: parsed rows as returned by ``_convert_import_data``
        :type data: list(list(str))
        :param import_fields: field names matching the data columns
        :type import_fields: list(str)
        :param match_configs: active configurations for the current model
        :type match_configs: recordset of ``base_import.match``
        :returns: (data, import_fields) with ``.id`` prepended when applicable
        :rtype: (list(list(str)), list(str))
        """
        Model = self.env[self.res_model]
        new_data = []
        any_match = False
        skipped = 0

        for row in data:
            row_values = dict(zip(import_fields, row, strict=False))
            db_id = self._find_matching_record(Model, row_values, match_configs)
            if db_id is None:
                # Ambiguous — skip row entirely (no create, no update).
                skipped += 1
                continue
            if db_id:
                any_match = True
            new_data.append([str(db_id) if db_id else ""] + list(row))

        if not any_match and not skipped:
            return data, import_fields

        if not any_match:
            # Some rows were skipped (ambiguous); the rest are creates.
            # Strip the prepended empty .id column before returning.
            return [row[1:] for row in new_data], import_fields

        _logger.info(
            "base_import_match: model %s — %d row(s) matched,"
            " %d skipped as ambiguous.",
            self.res_model,
            sum(1 for row in new_data if row[0]),
            skipped,
        )
        return new_data, [".id"] + list(import_fields)

    def _find_matching_record(self, Model, row_values, match_configs):
        """Return the database ID of the first unambiguous match, or False.

        Configurations are evaluated in *sequence* order.  For each one,
        **all** configured fields must be present and non-empty in the row
        (AND condition).  The search is skipped when any field value cannot
        be resolved (e.g. a many2one name that does not exist in the DB).

        :param Model: recordset of the target model (may be empty)
        :type Model: odoo.models.BaseModel
        :param row_values: mapping of ``{field_name: raw_string_value}``
        :type row_values: dict
        :param match_configs: active configurations ordered by sequence
        :type match_configs: recordset of ``base_import.match``
        :returns: database ID when exactly one record matches,
                  ``False`` when no record matches (create new),
                  ``None`` when multiple records match (skip row)
        :rtype: int or False or None
        """
        ambiguous = False
        for config in match_configs:
            if not config.field_ids:
                continue

            domain = []
            skip = False

            for field in config.field_ids:
                raw_value = row_values.get(field.name)

                if raw_value is None:
                    # Field not present in CSV — cannot determine match value.
                    skip = True
                    break

                if raw_value == "":
                    # Field present but empty — match records where it is also empty.
                    domain.append((field.name, "=", False))
                    continue

                resolved, ok = self._resolve_field_value(field, raw_value)
                if not ok:
                    skip = True
                    break

                domain.append((field.name, "=", resolved))

            if skip or not domain:
                continue

            try:
                records = Model.search(domain, limit=2)
            except Exception:
                _logger.exception(
                    "base_import_match: Error searching with domain %s" " on model %s.",
                    domain,
                    Model._name,
                )
                continue

            if len(records) == 1:
                _logger.debug(
                    "base_import_match: match found — model: %s,"
                    " config: '%s', record id: %d.",
                    Model._name,
                    config.name,
                    records.id,
                )
                return records.id

            if len(records) > 1:
                ambiguous = True
                _logger.warning(
                    "base_import_match: config '%s' returned %d records"
                    " on model %s for domain %s — row skipped.",
                    config.name,
                    len(records),
                    Model._name,
                    domain,
                )

        return None if ambiguous else False

    def _resolve_field_value(self, field, raw_value):
        """Convert a raw CSV string to a value usable in a search domain.

        For **many2one** fields the display name is resolved to a database
        ID via :meth:`~odoo.models.BaseModel.name_search`.  All other stored
        field types are returned as-is.

        :param field: field descriptor from the match configuration
        :type field: ``ir.model.fields`` record
        :param raw_value: raw string value as read from the import file
        :type raw_value: str
        :returns: ``(resolved_value, True)`` on success,
                  ``(None, False)`` when resolution fails
        :rtype: tuple(value, bool)
        """
        if field.ttype != "many2one":
            return raw_value, True

        RelModel = self.env[field.relation]
        try:
            results = RelModel.name_search(raw_value, operator="=", limit=2)
        except Exception:
            _logger.exception(
                "base_import_match: name_search failed on model %s" " with value '%s'.",
                field.relation,
                raw_value,
            )
            return None, False

        if len(results) == 1:
            return results[0][0], True

        if not results:
            _logger.debug(
                "base_import_match: no record found in '%s'" " with display name '%s'.",
                field.relation,
                raw_value,
            )
        else:
            _logger.warning(
                "base_import_match: ambiguous many2one — '%s' matches"
                " %d records in '%s'.",
                raw_value,
                len(results),
                field.relation,
            )

        return None, False
