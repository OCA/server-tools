# -*- coding: utf-8 -*-
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import html
from openerp import api, models


class IrFieldsConverter(models.Model):
    _inherit = "ir.fields.converter"

    @api.model
    def text_from_html(self, html_content, max_words=None, max_chars=None,
                       ellipsis=u"…"):
        """Extract text from an HTML field in a generator.

        :param str html_content:
            HTML contents from where to extract the text.

        :param int max_words:
            Maximum amount of words allowed in the resulting string.

        :param int max_chars:
            Maximum amount of characters allowed in the resulting string. If
            you apply this limit, beware that the last word could get cut in an
            unexpected place.

        :param str ellipsis:
            Character(s) to be appended to the end of the resulting string if
            it gets truncated after applying limits set in :param:`max_words`
            or :param:`max_chars`. If you want nothing applied, just set an
            empty string.
        """
        # Get words
        doc = html.fromstring(html_content)
        words = u"".join(doc.xpath("//text()")).split()

        # Truncate words
        suffix = max_words and len(words) > max_words
        if max_words:
            words = words[:max_words]

        # Get text
        text = u" ".join(words)

        # Truncate text
        suffix = suffix or max_chars and len(text) > max_chars
        if max_chars:
            text = text[:max_chars - (len(ellipsis) if suffix else 0)].strip()

        # Append ellipsis if needed
        if suffix:
            text += ellipsis

        return text
