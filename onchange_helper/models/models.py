# -*- coding: utf-8 -*-
# © 2016-2017 Akretion (http://www.akretion.com)
# © 2016-2017 Camptocamp (http://www.camptocamp.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


def _default_convert_to_record(field, value, record):
    return value


def _reference_convert_to_record(field, value, record):
    if isinstance(value, models.BaseModel):
        return value
    return value and record.env[value[0]].browse([value[1]])


def _relation_convert_to_record(field, value, record):
    if isinstance(value, models.BaseModel):
        return value
    return record.env[field.comodel_name]._browse(record.env, value)


_record_converter = {
    "reference": _reference_convert_to_record,
    "many2one": _relation_convert_to_record,
    "many2many": _relation_convert_to_record,
    "one2many": _relation_convert_to_record,
}


def _get_record_converter(field):
    return _record_converter.get(field.type, _default_convert_to_record)


def _convert_to_record(values_read, record):
    fields = record._fields
    result = {}
    for name, value in values_read.iteritems():
        if name in fields:
            field = fields[name]
            value = field.convert_to_cache(value, record, validate=False)
            value = _get_record_converter(field)(field, value, record)
            result[name] = value
    return result


@api.model
def _get_new_values(self, record, on_change_result):
    vals = on_change_result.get("value", {})
    new_values = {}
    for fieldname, value in vals.iteritems():
        if fieldname not in record:
            column = self._fields[fieldname]
            if value and column.type == "many2one":
                value = value[0]  # many2one are tuple (id, name)
            new_values[fieldname] = value
    return new_values


@api.model
def play_onchanges(self, values, onchange_fields):
    # _onchange_spec returns only api.v7 onchanges
    onchange_specs = self._onchange_spec()
    # api v8
    for key in self._onchange_methods.keys():
        onchange_specs[key] = "true"
    # we need all fields in the dict even the empty ones
    # otherwise 'onchange()' will not apply changes to them
    all_values = values.copy()

    # If self is a record (play onchange on existing record)
    # we take the value of the field
    # If self is an empty record we will have an empty value
    if self:
        self.ensure_one()
        record_values = self._convert_to_write(
            _convert_to_record(self.read()[0], self)
        )
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
        f: v
        for f, v in all_values.iteritems()
        if not (self._fields[f].compute and not self._fields[f].inverse)
        and (f in values or f in new_values)
    }


class IrRule(models.Model):
    _inherit = "ir.rule"

    def _setup_complete(self, cr, uid):
        if not hasattr(models.BaseModel, "play_onchanges"):
            setattr(models.BaseModel, "play_onchanges", play_onchanges)
            setattr(models.BaseModel, "_get_new_values", _get_new_values)
        return super(IrRule, self)._setup_complete(cr, uid)
