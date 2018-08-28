# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools import pycompat


class Base(models.AbstractModel):
    _inherit = 'base'

    def default_dependant_get(self, fields_list, vals):
        """ default_get(fields) -> default_values
        Return default values for the fields in ``fields_list``. Default
        values are determined by the context, user defaults, and the model
        itself.
        :param fields_list: a list of field names
        :param vals: A list of the creation values
        :return: a dictionary mapping each field name to its corresponding
            default value, if it has one.
        """
        # trigger view init hook
        self.view_init(fields_list)
        defaults = {}
        for name in fields_list:
            field = self._fields.get(name)
            default = False
            if field.default:
                default = field.default(self)
            val = vals.get(name, default)
            if field and field.dependant_default and (
                not val or (default and default == val)
            ):
                defaults[name] = getattr(self, field.dependant_default)(vals)
        # convert default values to the right format
        defaults = self._convert_to_write(defaults)

        return defaults

    @api.model
    def _add_missing_default_values(self, values):
        vals = super()._add_missing_default_values(values)
        # compute missing fields
        missing_dependant_defaults = {
            name
            for name, field in self._fields.items()
            if getattr(field, 'dependant_default', False)
        }
        if not missing_dependant_defaults:
            return vals
        # override values with the provided values
        defaults = self.default_dependant_get(
            list(missing_dependant_defaults), vals)
        for name, value in defaults.items():
            if self._fields[name].type == 'many2many' and value and isinstance(
                    value[0], pycompat.integer_types):
                # convert a list of ids into a list of commands
                defaults[name] = [(6, 0, value)]
            elif self._fields[
                name].type == 'one2many' and value and isinstance(value[0],
                                                                  dict):
                # convert a list of dicts into a list of commands
                defaults[name] = [(0, 0, x) for x in value]
        vals.update(defaults)
        return vals
