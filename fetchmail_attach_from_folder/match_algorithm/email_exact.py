# Copyright - 2013-2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tools.mail import email_normalize, email_split
from odoo.tools.safe_eval import safe_eval


class EmailExact:
    """Search for exactly the email address as noted in the email."""

    def _get_mailaddresses(self, folder, message_dict):
        mailaddresses = []
        fields = folder.mail_field.split(",")
        for field in fields:
            if field in message_dict:
                mailaddresses += email_split(message_dict[field])
        # Normalize using email_normalize for consistent matching.
        # This strips display names, lowercases the address, and handles
        # edge cases (e.g. "<user@domain.com>" or "User <user@domain.com>").
        return [email_normalize(addr) or addr.lower() for addr in mailaddresses]

    def _get_mailaddress_search_domain(
        self, folder, message_dict, operator="=ilike", values=None
    ):
        """Build search domain for email matching.

        We use ``=ilike`` (case-insensitive exact match) instead of ``=``
        so that uppercase email variants (e.g. ``Name.SURNAME@Domain.com``)
        also match partners whose email is stored in mixed case.

        ``=ilike`` is safe here because there are no ``%`` wildcards in the
        search values, so it behaves exactly like a case-insensitive ``=``
        (PostgreSQL: ``LOWER(field) = LOWER(value)``).
        """
        mailaddresses = values or self._get_mailaddresses(folder, message_dict)
        if not mailaddresses:
            return [(0, "=", 1)]
        search_domain = (
            (["|"] * (len(mailaddresses) - 1))
            + [(folder.model_field, operator, addr) for addr in mailaddresses]
            + safe_eval(folder.domain or "[]")
        )
        return search_domain

    def search_matches(self, folder, message_dict):
        """Returns recordset of matching objects."""
        object_model = folder.env[folder.model_id.model]
        search_domain = self._get_mailaddress_search_domain(folder, message_dict)
        return object_model.search(search_domain, order=folder.model_order)
