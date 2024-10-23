# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, models
from odoo.exceptions import ValidationError


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    @api.constrains("source", "value")
    def _constrains_value(self):
        """In general we allow to have different html structure... TODO"""
        if not self.env.context.get("skip_translations_checks"):
            for term in self:
                if term.value:
                    term._check_new_formatting()
                    term._check_old_formatting()
                    term._check_html()

    def _check_html(self):
        regex = re.compile(r"<.+?>")
        msg = _("There is a discrepancy in html tags.")
        self._check_regex_matches(regex, msg)

    def _check_new_formatting(self):
        regex = re.compile(r"{.*?}")
        msg = _("There is a discrepancy in new format string variables.")
        self._check_regex_matches(regex, msg)

    def _check_old_formatting(self):
        regex = re.compile(r"%(?:\(\w+\))?[dsr]", re.ASCII)
        msg = _("There is a discrepancy in old format string variables.")
        self._check_regex_matches(regex, msg)

    def _check_regex_matches(self, regex, msg):
        self.ensure_one()
        src_matches = regex.findall(self.src)
        dst_matches = regex.findall(self.value)
        correct = len(src_matches) == len(dst_matches)
        correct &= all(s == d for s, d in zip(src_matches, dst_matches))
        if not correct:
            msg_source = _("Source: %s") % self.src
            msg_value = _("Value: %s") % self.value
            raise ValidationError("\n".join([msg, msg_source, msg_value]))
