# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _read_group_fill_results(self, domain, groupby,
                                 remaining_groupbys, aggregated_fields,
                                 count_field, read_group_result,
                                 read_group_order=None):
        """
        This method checks if the 'group_full' property is present
        in Selection field.
        It accepts:
        True : each value of the Selection will appear
        A list of values : the values to show
        """
        field = self._fields.get(groupby)
        if field and isinstance(field, fields.Selection) and field.group_full:
            VALUES_DICT = dict(field.selection)
            if isinstance(field.group_full, bool):
                remaining_groups = [key for key in dict(field.selection)]
            elif isinstance(field.group_full, list):
                remaining_groups = list(field.group_full)
            else:
                remaining_groups = []
            for result in read_group_result:
                field_value = result[groupby]
                result[groupby] = (field_value, VALUES_DICT.get(field_value))
                if field_value in remaining_groups:
                    remaining_groups.remove(field_value)

            for group in remaining_groups:
                # Selection field that we want to appear in group but
                # with count == 0
                read_group_result.append({groupby: group, 'count': 0,
                                          'domain': [(groupby, '=', group)]})

        return super(BaseModel, self)._read_group_fill_results(
            domain, groupby, remaining_groupbys, aggregated_fields,
            count_field, read_group_result, read_group_order
        )
