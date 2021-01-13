# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields


class Many2manyCustom(fields.Many2many):
    """Many2manyCustom field is intended to customize Many2many properties.

    :param create_table: defines if the relational table must be created
    at the initialization of the field (boolean)
    """

    _slots = {"create_table": True}

    def update_db(self, model, columns):
        if not self.create_table:
            return
        return super().update_db(model, columns)


fields.Many2manyCustom = Many2manyCustom
