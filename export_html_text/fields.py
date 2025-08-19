# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Field
from odoo.tools import html2plaintext

_ORIG_convert_to_export = Field.convert_to_export


def _convert_to_export_patched(self, value, record):
    content = _ORIG_convert_to_export(self, value, record)
    if (
        self.type == "html"
        and content
        and record.env.context.get("export_html_as_text")
    ):
        return html2plaintext(content)
    return content


Field.convert_to_export = _convert_to_export_patched
