# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from ..utils import to_tsquery


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        query = super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )
        if not order and not count:
            # If no order is specified and a full text search argument is found
            # order by the full text search rank
            for arg in args:
                if isinstance(arg, (tuple, list)) and arg[1] == "@@":
                    field = self._fields.get(arg[0])
                    if field:
                        if field.inherited:
                            field = field.base_field
                        if field.store and field.column_type:
                            qualifield_name = self._inherits_join_calc(
                                self._table, arg[0], query
                            )
                            query.order = (
                                f"ts_rank_cd({qualifield_name}, "
                                f"{to_tsquery(arg[2], field.dictionary)}) desc, "
                                f"{query.order}"
                            )
        return query
