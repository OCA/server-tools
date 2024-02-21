# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from markupsafe import Markup

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _render_template(self, template, values=None):
        result = super()._render_template(template, values)
        result_str = str(result)
        lang_code = "en_US"
        request = values.get("request")
        if request:
            # For views
            lang_code = request.env.lang
        else:
            # For reports
            lang_match = re.search(r'data-oe-lang="([^"]+)"', result_str)
            if lang_match:
                lang_code = lang_match.group(1)
        view = self._get(template).sudo()
        content_mappings = (
            self.env["template.content.mapping"]
            .sudo()
            .search(
                [
                    ("template_id", "=", view.id),
                    "|",
                    ("lang", "=", lang_code),
                    ("lang", "=", False),
                ]
            )
        )
        if content_mappings:
            for mapping in content_mappings:
                content_from = mapping.content_from
                content_to = mapping.content_to or ""
                result_str = result_str.replace(content_from, content_to)
            result = Markup(result_str)
        return result
