# Copyright - 2013-2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tools.mail import email_split
from odoo.tools.safe_eval import safe_eval


class EmailExact:
    """Search for exactly the mailadress as noted in the email"""

    def _get_mailaddresses(self, folder, message_dict):
        mailaddresses = []
        fields = folder.mail_field.split(",")
        for field in fields:
            if field in message_dict:
                mailaddresses += email_split(message_dict[field])
        return [addr.lower() for addr in mailaddresses]

    def _get_mailaddress_search_domain(
        self, folder, message_dict, operator="=", values=None
    ):
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
        matches = object_model.search(search_domain, order=folder.model_order)
        return matches.ids
