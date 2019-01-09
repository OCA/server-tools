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
            if fieldname not in record:
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
            clean_new_values = self.clean_o2m_m2o_m2m_fields(new_values)
            all_values.update(clean_new_values)

        return {
            f: v for f, v in all_values.iteritems()
            if not self._fields[f].compute
            and (f in values or f in new_values)}

    @api.multi
    def clean_o2m_m2o_m2m_fields(self, vals):
        """The dict returned by onchange method fill o2m fields inside a tuple
        ( eg.: 'tax_line_ids': [(5,), (0, 0, {'account_id': (14, u'111200
        Tax Received')})] ), but if you want write the value it need to
        be an integer not a tuple ( eg.: 'tax_line_ids': [(5,),
        (0, 0, {'account_id': 14 })] ) or you receive error, the method below
         try to solve the problem
        """
        for itens in vals:
            if type(vals.get(itens)) is list:
                index = 1
                while index < len(vals.get(itens)):
                    for value in vals.get(itens)[index]:
                        if type(value) is dict:
                            for item in value:
                                if type(value.get(item)) is tuple:
                                    value[item] = value.get(item)[0]
                    index += 1
        return vals
