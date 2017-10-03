# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import ISQLQuote


class IdentifierAdapter(ISQLQuote):
    def __init__(self, identifier, quote=True):
        self.quote = quote
        self.identifier = identifier

    def __conform__(self, protocol):
        if protocol == ISQLQuote:
            return self

    def getquoted(self):
        def is_identifier_char(c):
            return c.isalnum() or c in ['_', '$']

        format_string = '"%s"'
        if not self.quote:
            format_string = '%s'
        return format_string % ''.join(
            filter(is_identifier_char, self.identifier)
        )
