# Copyright 2016-2017 Akretion (http://www.akretion.com)
# Copyright 2016-2017 Camptocamp (http://www.camptocamp.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _get_new_values(self, record, on_change_result):
        vals = on_change_result.get('value', {})
        new_values = {}
        for fieldname, value in vals.items():
            if fieldname not in record:
                column = self._fields[fieldname]
                if value and column.type == 'many2one':
                    value = value[0]  # many2one are tuple (id, name)
                new_values[fieldname] = value
        return new_values

    @api.model
    def play_onchanges(self, values, onchange_fields):
        """
        :param values: dict of input value that
        :param onchange_fields: fields for which onchange methods will be
        played
        Order in onchange_fields is very important as onchanges methods will
        be played in that order.
        :return: changed values
        """
        # _onchange_spec() will return onchange fields from the default view
        # we need all fields in the dict even the empty ones
        # otherwise 'onchange()' will not apply changes to them
        onchange_specs = {
            field_name: '1' for field_name, field in self._fields.items()
        }
        all_values = values.copy()
        # If self is a record (play onchange on existing record)
        # we take the value of the field
        # If self is an empty record we will have an empty value
        if self:
            self.ensure_one()
            record_values = self._convert_to_write(
                {
                    field_name: self[field_name]
                    for field_name, field in self._fields.items()
                }
            )
        else:
            # We get default values, they may be used in onchange
            record_values = self.default_get(self._fields.keys())
        for field in self._fields:
            if field not in all_values:
                all_values[field] = record_values.get(field, False)

        new_values = {}
        for field in onchange_fields:
            onchange_values = self.onchange(all_values, field, onchange_specs)
            new_values.update(self._get_new_values(values, onchange_values))
            all_values.update(new_values)

        return {
            f: v
            for f, v in all_values.items()
            if not (self._fields[f].compute and not self._fields[f].inverse)
            and (f in values or f in new_values or f in onchange_fields)
        }
