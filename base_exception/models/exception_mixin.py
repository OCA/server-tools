# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExceptionMixin(models.AbstractModel):
    _name = "exception.mixin"
    _description = "Exception Mixin"

    exception_ids = fields.Many2many("exception.rule")
    ignore_exception = fields.Boolean("Ignore Exceptions", copy=False)
