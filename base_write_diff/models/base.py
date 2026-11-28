# Copyright 2025 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import Command, models
from odoo.tools.misc import frozendict

from odoo.addons.web.models.models import RecordSnapshot


class BaseModel(models.BaseModel):
    _inherit = "base"

    def write(self, vals):
        # OVERRIDE: when using the ``write_use_diff_values`` context key, remove values
        # that won't be changed before/after the ``write()`` itself.
        # If ``write()`` is called on an empty recordset or with no value, ignore
        # everything and shortcut to ``super()``.
        if not (self and vals and self.env.context.get("write_use_diff_values")):
            return super().write(vals)
        recs_by_vals = defaultdict(lambda: self.browse())
        for rec in self:
            recs_by_vals[frozendict(rec._get_write_diff_values(vals))] += rec
        for rec_vals, recs in recs_by_vals.items():
            if rec_vals:  # Don't trigger ``write()`` if there is nothing to update
                super(BaseModel, recs).write(dict(rec_vals))
        return True

    def write_diff(self, vals: dict) -> bool:
        """Executes a ``write()`` only on fields that actually need to be updated"""
        return self.with_context(write_use_diff_values=True).write(vals)

    def _get_write_diff_values(self, vals: dict) -> dict:
        """Compares record values with the values to write

        Returns a dictionary containing only the fields that actually needs to be
        updated on ``self``, filtering out those which contain a value that is the same
        as the current record's field value.
        For example:
            >>> self.name = "A"
            >>> self.code = "a"
            >>> self._get_write_diff_values({"name": "A", "code": "a"})
            {}
            >>> self._get_write_diff_values({"name": "B", "code": "a"})
            {"name": "B"}
            >>> self._get_write_diff_values({"name": "B", "code": "b"})
            {"name": "B", "code": "b"}
        """
        self.ensure_one()
        diff_values = {}

        # Step 1: group fields according to whether they're multi-relational or not
        x2many_fields_values, simple_fields_values = {}, {}
        for fname, fvalue in vals.items():
            if self._fields[fname].type in ("one2many", "many2many"):
                x2many_fields_values[fname] = fvalue
            else:
                simple_fields_values[fname] = fvalue

        # Step 2: prepare fields to update by checking simple fields first
        if simple_fields_values:
            simple_fields_specs = {f: {} for f in simple_fields_values}
            snapshot0 = self._do_snapshot({}, simple_fields_specs)
            snapshot1 = self._do_snapshot(simple_fields_values, simple_fields_specs)
            diff_values.update(snapshot1.diff(snapshot0))

        # Step 3: prepare fields to update by checking multi-relational fields
        # For each multi-relational field, prepare a new list of values by checking
        # the original commands:
        # - if it's an update command, check whether something actually changes on
        #   the corecord by calling ``_get_write_diff_values()`` recursively
        # - else, add the original command to the new list: all commands except "update"
        #   will modify the record-corecords relation by creating/[un]linking/deleting
        #   corecords
        # Then, check the new list of values to decide if the field needs updating:
        # - at least 1 creation/update => add the full list of commands for simplicity
        # - else => check whether the new values will effectively change the
        #   record-corecords relationship
        for fname, fvalues in x2many_fields_values.items():
            # Prepare the new list of commands/values according to the original command
            new_fvalues = []
            for fvalue in fvalues:
                if fvalue[0] == Command.UPDATE:
                    cmd, corec_id, corec_vals = fvalue
                    corec = self.env[self._fields[fname].comodel_name].browse(corec_id)
                    if corec_diff_vals := corec._get_write_diff_values(corec_vals):
                        new_fvalues.append((cmd, corec_id, corec_diff_vals))
                else:
                    new_fvalues.append(fvalue)
            # Check whether we actually need to include the new list in the diff values
            if any(v[0] in (Command.CREATE, Command.UPDATE) for v in new_fvalues):
                diff_values[fname] = new_fvalues
            else:
                x2many_snapshot0 = self._do_snapshot({}, {fname: {}})
                x2many_snapshot1 = self._do_snapshot({fname: new_fvalues}, {fname: {}})
                if x2many_diff_values := x2many_snapshot1.diff(x2many_snapshot0):
                    diff_values.update(x2many_diff_values)

        return diff_values

    def _do_snapshot(self, vals: dict, specs: dict) -> "RecordSnapshot":
        """Prepares a ``RecordSnapshot`` object with the specified params"""
        self.ensure_one()
        # Align ``vals`` and ``specs`` to make sure they both contain the same fields:
        # - if a field in ``specs`` is missing from ``vals``, we read its current value
        #   from the record and convert it to a ``write()``-able format to prevent cache
        #   issues and inconsistencies
        # - if a field in ``vals`` is missing from ``specs``, we add it with the default
        #   value of ``{}`` to allow ``RecordSnapshot`` to handle it properly
        vals_fnames_not_in_specs = set(vals) - set(specs)
        specs_fnames_not_in_vals = set(specs) - set(vals)
        for fname in vals_fnames_not_in_specs:
            specs[fname] = {}
        for fname in specs_fnames_not_in_vals:
            vals[fname] = self._fields[fname].convert_to_write(self[fname], self)
        return RecordSnapshot(self.new(values=vals, origin=self), fields_spec=specs)
