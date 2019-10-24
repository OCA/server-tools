# -*- coding: utf-8 -*-
# © 2016-2017 Akretion (http://www.akretion.com)
# © 2016-2017 Camptocamp (http://www.camptocamp.com/)
# © 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _compute_onchange_dirty(
        self, original_record, modified_record, fieldname_onchange=None
    ):
        """
        Return the list of dirty fields. (designed to be called by
        play_onchanges)
        The list of dirty fields is computed from the list marked as dirty
        on the record. Form this list, we remove the fields for which the value
        into the original record is the same as the one into the current record
        :param original_record:
        :return: changed values
        """
        dirties = []
        if fieldname_onchange:
            for field_name, field in modified_record._fields.items():
                # special case. We consider that a related field is modified
                # if a modified field is in the first position of the path
                # to traverse to get the value.
                if field.related and field.related[0].startswith(
                    fieldname_onchange
                ):
                    dirties.append(field_name)
        for field_name in modified_record._get_dirty():
            original_value = original_record[field_name]
            new_value = modified_record[field_name]
            if original_value == new_value:
                continue
            dirties.append(field_name)
        for field_name, field in modified_record._fields.items():
            if not field.store:
                continue
            new_value = modified_record[field_name]
            if field.type not in ("one2many", "many2many"):
                continue
            # if the field is a one2many or many2many, check that any
            # item is a new Id
            if models.NewId in [type(i.id) for i in new_value]:
                dirties.append(field_name)
                continue
            # if the field is a one2many or many2many, check if any item
            # is dirty
            for r in new_value:
                if r._get_dirty():
                    ori = [
                        r1
                        for r1 in original_record[field_name]
                        if r1.id == r.id
                    ][0]
                    # if fieldname_onchange is None avoid recurssion...
                    if fieldname_onchange and self._compute_onchange_dirty(
                        ori, r
                    ):
                        dirties.append(field_name)
                        break
        return dirties

    def _convert_to_onchange(self, record, field, value):
        if field.type == "many2one":
            # for many2one, we keep the id and don't call the
            # convert_on_change to avoid the call to name_get by the
            # convert_to_onchange
            if value.id:
                return value.id
            return False
        elif field.type in ("one2many", "many2many"):
            result = [(5,)]
            for record in value:
                vals = {}
                # We have to check first if the record already exists
                # (only in case of M2M).
                if field.type == "many2many" and not isinstance(
                        record.id, models.NewId):
                    result.append((4, record.id))
                    continue
                for name in record._cache:
                    if name in models.LOG_ACCESS_COLUMNS:
                        continue
                    v = record[name]
                    f = record._fields[name]
                    if f.type == "many2one" and isinstance(v.id, models.NewId):
                        continue
                    vals[name] = self._convert_to_onchange(record, f, v)
                if not record.id:
                    result.append((0, 0, vals))
                elif vals:
                    result.append((1, record.id, vals))
                else:
                    result.append((4, record.id))
            return result
        else:
            return field.convert_to_onchange(value, record, [field.name])

    def play_onchanges(self, values, onchange_fields=None):
        """
        Play the onchange methods defined on the current record and return the
        changed values.
        The record is not modified by the onchange.

        The intend of this method is to provide a way to get on the server side
        the values returned by the onchange methods when called by the UI.
        This method is useful in B2B contexts where records are created or
        modified from server side.

        The returned values are those changed by the execution of onchange
        methods registered for the onchange_fields according to the provided
        values. As consequence, the result will not contain the modifications
        that could occurs by the execution of compute methods registered for
        the same onchange_fields.

        It's on purpose that we avoid to trigger the compute methods for the
        onchange_fields. These compute methods will be triggered when calling
        the create or write method. In this way we avoid to compute useless
        information.


        :param values: dict of input value that
        :param onchange_fields: fields for which onchange methods will be
        played. If not provided, the list of field is based on the values keys.
        Order in onchange_fields is very important as onchanges methods will
        be played in that order.
        :return: changed values

        This method reimplement the onchange method to be able to work on the
        current recordset if provided.
        """
        updated_values = values.copy()
        env = self.env
        if self:
            self.ensure_one()

        if not onchange_fields:
            onchange_fields = values.keys()

        elif not isinstance(onchange_fields, list):
            onchange_fields = [onchange_fields]

        if not onchange_fields:
            onchange_fields = values.keys()

        # filter out keys in field_onchange that do not refer to actual fields
        names = [n for n in onchange_fields if n in self._fields]

        # create a new record with values, and attach ``self`` to it
        with env.do_in_onchange():
            # keep a copy of the original record.
            # attach ``self`` with a different context (for cache consistency)
            origin = self.with_context(__onchange=True)
            origin_dirty = set(self._get_dirty())
            fields.copy_cache(self, origin.env)
            if self:
                record = self
                record.update(values)
            else:
                # initialize with default values, they may be used in onchange
                new_values = self.default_get(self._fields.keys())
                new_values.update(values)
                record = self.new(new_values)
            values = {name: record[name] for name in record._cache}
            record._origin = origin

        # determine which field(s) should be triggered an onchange
        todo = list(names) or list(values)
        done = set()

        # dummy assignment: trigger invalidations on the record
        with env.do_in_onchange():
            for name in todo:
                if name == "id":
                    continue
                value = record[name]
                field = self._fields[name]
                if field.type == "many2one" and field.delegate and not value:
                    # do not nullify all fields of parent record for new
                    # records
                    continue
                record[name] = value

        dirty = set()

        # process names in order (or the keys of values if no name given)
        while todo:
            name = todo.pop(0)
            if name in done:
                continue
            done.add(name)

            with env.do_in_onchange():
                # apply field-specific onchange methods
                record._onchange_eval(name, "1", {})

                # determine which fields have been modified
                dirties = self._compute_onchange_dirty(origin, record, name)
                dirty |= set(dirties)
                todo.extend(dirties)

                # preserve values to update since these are the one selected
                # by the user.
                for f in dirties:
                    field = self._fields[f]
                    if (f in updated_values and
                            field.type not in ("one2many", "many2many")):
                        record[f] = values[f]

        # prepare the result to return a dictionary with the new values for
        # the dirty fields
        result = {}
        for name in dirty:
            field = self._fields[name]
            value = record[name]
            if field.type == "many2one" and isinstance(value.id, models.NewId):
                continue
            result[name] = self._convert_to_onchange(record, field, value)

        # reset dirty values into the current record
        if self:
            to_reset = dirty | set(values.keys())
            with env.do_in_onchange():
                for name in to_reset:
                    original = origin[name]
                    new = self[name]
                    if original == new:
                        continue
                    self[name] = origin[name]
                    env.dirty[record].discard(name)
            env.dirty[record].update(origin_dirty)
        return result
