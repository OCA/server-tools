# -*- coding: utf-8 -*-
# Copyright 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import logging
from lxml import etree, html
from openerp import api, models

_logger = logging.getLogger(__name__)


class IrFieldsConverter(models.Model):
    _inherit = "ir.fields.converter"

    @api.model
    def imgs_from_html(self, html_content, limit=None, fail=False):
        """Extract all images in order from an HTML field in a generator.

        :param str html_content:
            HTML contents from where to extract the images.

        :param int limit:
            Only get up to this number of images.

        :param bool fail:
            If ``True``, exceptions will be raised.
        """
        # Parse HTML
        try:
            doc = html.fromstring(html_content)
        except (TypeError, etree.XMLSyntaxError, etree.ParserError):
            if fail:
                raise
            else:
                _logger.exception("Failure parsing this HTML:\n%s",
                                  html_content)
                return

        # Required tools
        query = """
            //img[@src] |
            //*[contains(translate(@style, "BACKGROUND", "background"),
                         'background')]
               [contains(translate(@style, "URL", "url"), 'url(')]
        """
        rgx = r"""
            url\(\s*        # Start function
            (?P<url>[^)]*)  # URL string
            \s*\)           # End function
        """
        rgx = re.compile(rgx, re.IGNORECASE | re.VERBOSE)

        # Loop through possible image URLs
        for lap, element in enumerate(doc.xpath(query)):
            if limit and lap >= limit:
                break
            if element.tag == "img":
                yield element.attrib["src"]
            else:
                for rule in element.attrib["style"].split(";"):
                    # Extract background image
                    parts = rule.split(":", 1)
                    try:
                        if parts[0].strip().lower() in {"background",
                                                        "background-image"}:
                            yield (rgx.search(parts[1])
                                   .group("url").strip("\"'"))
                    # Malformed CSS or no match for URL
                    except (IndexError, AttributeError):
                        pass
