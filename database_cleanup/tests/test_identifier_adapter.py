from odoo.tests import TransactionCase

from odoo.addons.database_cleanup.identifier_adapter import IdentifierAdapter


class TestIdentifierAdapter(TransactionCase):
    def test_column_name_with_spaces(self):
        """Spaces in column names are preserved except in unquoted identifiers."""
        self.assertEqual(
            self.env.cr.mogrify("%s", (IdentifierAdapter("snailmail_cover "),)),
            b'"snailmail_cover "',
        )
        self.assertEqual(
            self.env.cr.mogrify(
                "%s", (IdentifierAdapter("snailmail_cover ", quote=False),)
            ),
            b"snailmail_cover",
        )
