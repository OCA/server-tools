# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError


class BaseExceptionError(ValidationError):
    def __init__(self, msg, rules_to_add, rules_to_remove):
        super().__init__(msg)
        self.rules_to_add = rules_to_add
        self.rules_to_remove = rules_to_remove
