# Copyright (C) 2021 Akretion (<http://www.akretion.com>).
# @author Florian Mounier <florian.mounier@akretion.com>
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from random import choice
from string import ascii_lowercase, ascii_uppercase, digits

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class CodeFormatMixin(models.AbstractModel):
    _name = "code.format.mixin"
    _description = "Customizable code format Mixin"

    #  1/ _code_mask must be added in the related model
    # e.g. in "gift.card":
    #     _code_mask = {
    #       "mask": "code_mask",
    #       "template": "gift_card_tmpl_id"
    #      }

    # 2/ In addition, update a method of the target model to
    # compute the code. For example the create method:
    #     @api.model
    #     def create(self, vals):
    #         res = super().create(vals)
    #         vals["code"] = res._generate_code()

    _code_mask = {}

    _default_mask = "XXXXXX-00"
    _forbidden_characters = "iI1oO0"
    _dedup_max_retries = 20

    def _generate_code(self):
        choices = self._get_choice_collections()
        for rec in self:
            mask = rec._get_mask()
            code = rec._generate_code_from_mask(choices, mask)
            retries = 0
            while len(self.search([("code", "=", code)])):
                code = rec._generate_code_from_mask(choices, mask)
                retries += 1
                if retries > self._dedup_max_retries:
                    raise ValidationError(
                        _("Unable to generate a non existing random code.")
                    )
            return code

    code = fields.Char(compute=_generate_code, readonly=True, store=True)

    def _get_mask(self):
        return self[self._code_mask["template"]][self._code_mask["mask"]]

    def _generate_mask(self, mask):
        if not mask:
            mask = self._default_mask
        return mask

    def _generate_code_from_mask(self, choices, mask):
        def unmask(char):
            char_collection = choices.get(char)
            if char_collection:
                return choice(char_collection)
            return char

        final_mask = self._generate_mask(mask)
        return "".join(unmask(char) for char in final_mask)

    def _get_choice_collections(self):
        # x means a random lowercase letter
        # X means a random uppercase letter
        # 0 means a random digit
        return {
            "X": [
                char
                for char in ascii_uppercase
                if char not in self._forbidden_characters
            ],
            "x": [
                char
                for char in ascii_lowercase
                if char not in self._forbidden_characters
            ],
            "0": digits,
        }
