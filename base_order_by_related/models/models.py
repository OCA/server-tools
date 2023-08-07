# Copyright (C) 2023 Therp (<http://www.therp.nl>).
# @author Tom Blauwendraat <tblauwendraat@therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class BaseModel(models.AbstractModel):
    _inherit = "base"

    _order_by_related = []

    @api.model
    def _related_join_calc(self, alias, fname, query):
        model, field = self, self._fields[fname]
        while field.related:
            # retrieve the parent model where field is inherited from
            if field.related_field.model_name not in self.env:
                continue
            related_model = self.env[field.related_field.model_name]
            if len(field.related) == 1:
                related_fname = "id"
                related_fname2 = field.related[0]
            else:
                related_fname = field.related[0]
                related_fname2 = field.related[1]

            # JOIN related_model._table AS related_alias ON
            # alias.related_fname = related_alias.id
            related_alias = query.left_join(
                alias,
                related_fname,
                related_model._table,
                "id",
                related_fname2,
            )
            model, alias, field = related_model, related_alias, field.related_field
        # handle the case where the field is translated
        if field.translate is True:
            return model._generate_translated_field(alias, related_fname2, query)
        else:
            return '"%s"."%s"' % (alias, related_fname2)

    @api.model
    def _generate_order_by_inner(
        self, alias, order_spec, query, reverse_direction=False, seen=None
    ):
        order_parts = order_spec.split(",")
        order_fields = [p.strip().split(" ")[0].strip() for p in order_parts]
        if not any(f in self._order_by_related for f in order_fields):
            return super()._generate_order_by_inner(
                alias, order_spec, query, reverse_direction=reverse_direction, seen=seen
            )

        if seen is None:
            seen = set()
        self._check_qorder(order_spec)

        order_by_elements = []
        for order_part in order_parts:
            order_split = order_part.strip().split(" ")
            order_field = order_split[0].strip()
            if order_field not in self._order_by_related:
                order_by_elements += super()._generate_order_by_inner(
                    alias,
                    order_part,
                    query,
                    reverse_direction=reverse_direction,
                    seen=seen,
                )
                continue

            self._fields.get(order_field)
            order_direction = (
                order_split[1].strip().upper() if len(order_split) == 2 else ""
            )
            if reverse_direction:
                order_direction = "ASC" if order_direction == "DESC" else "DESC"
            qualified_name = self._related_join_calc(alias, order_field, query)
            order_by_elements.append("%s %s" % (qualified_name, order_direction))
        return order_by_elements

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        ret = super().fields_get(allfields=allfields, attributes=attributes)
        for k in self._order_by_related:
            if k in ret:
                ret[k]["sortable"] = True
        return ret
