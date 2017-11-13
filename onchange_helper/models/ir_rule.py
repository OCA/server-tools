# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


def get_new_values(model, record, on_change_result):
    vals = on_change_result.get('value', {})
    new_values = {}
    for fieldname, value in vals.iteritems():
        if fieldname not in record:
            column = model._fields[fieldname]
            if value and column.type == 'many2one':
                value = value[0]  # many2one are tuple (id, name)
            new_values[fieldname] = value
    return new_values


@api.model
def play_onchanges(self, values, onchange_fields):
    onchange_specs = self._onchange_spec()
    # we need all fields in the dict even the empty ones
    # otherwise 'onchange()' will not apply changes to them
    all_values = values.copy()
    for field in self._fields:
        if field not in all_values:
            all_values[field] = False

    # we work on a temporary record
    new_record = self.new(all_values)

    new_values = {}
    for field in onchange_fields:
        onchange_values = new_record.onchange(all_values,
                                              field, onchange_specs)
        new_values.update(get_new_values(self, values, onchange_values))
        all_values.update(new_values)

    res = {f: v for f, v in all_values.iteritems()
           if f in values or f in new_values}
    return res


class IrRule(models.Model):
    _inherit = 'ir.rule'

    def _setup_complete(self, cr, uid):
        if not hasattr(models.BaseModel, 'play_onchanges'):
            setattr(models.BaseModel, 'play_onchanges', play_onchanges)
        return super(IrRule, self)._setup_complete(cr, uid)
