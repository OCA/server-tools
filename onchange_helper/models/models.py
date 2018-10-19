# -*- coding: utf-8 -*-
# © 2016-2017 Akretion (http://www.akretion.com)
# © 2016-2017 Camptocamp (http://www.camptocamp.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _get_new_values(self, record, on_change_result):
        vals = on_change_result.get('value', {})
        new_values = {}
        for fieldname, value in vals.iteritems():
            # if overwrite_values is True values record are owerited with
            # on_change_result
            if fieldname not in record or\
                    self.env.context.get('overwrite_values'):
                column = self._fields[fieldname]
                if value and column.type == 'many2one':
                    value = value[0]  # many2one are tuple (id, name)
                new_values[fieldname] = value
        return new_values

    def play_onchanges(self, values, onchange_fields):
        onchange_specs = self._onchange_spec()
        # we need all fields in the dict even the empty ones
        # otherwise 'onchange()' will not apply changes to them
        all_values = values.copy()

        # If self is a record (play onchange on existing record)
        # we take the value of the field
        # If self is an empty record we will have an empty value
        if self:
            self.ensure_one()
            record_values = self._convert_to_write(self.read()[0])
        else:
            record_values = {}
        for field in self._fields:
            if field not in all_values:
                all_values[field] = record_values.get(field, False)

        new_values = {}
        for field in onchange_fields:
            onchange_values = self.onchange(all_values, field, onchange_specs)
            new_values.update(self._get_new_values(values, onchange_values))
            all_values.update(new_values)

        return {
            f: v for f, v in all_values.iteritems()
            if not self._fields[f].compute
            and (f in values or f in new_values)}
