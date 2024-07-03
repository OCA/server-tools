# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv.expression import OR


class SearchMultiValueMixin(models.AbstractModel):

    _name = "search.multi.value.mixin"
    _description = "Mixin to allow delimiter-separated searches"

    search_multi = fields.Char(
        "Multiple search",
        compute="_compute_search_multi",
        search="_search_multi",
    )

    def _compute_search_multi(self):
        self.update({"search_multi": False})

    @api.model
    def _get_search_fields_multi_value(self):
        raise NotImplementedError

    def _search_multi(self, operator, value):
        if operator == "=" or operator == "ilike":
            operator = "in"
            comparator = OR
        else:
            raise UserError(_("Operator %s is not usable with multisearch", operator))

        value_list = value.split(" ") if " " in value else [value]
        search_fields = self._get_search_fields_multi_value()
        domain_list = []
        for search_field in search_fields:
            domain_search_field = [(search_field, operator, tuple(value_list))]
            domain_list.append(domain_search_field)
        return comparator(domain_list)
