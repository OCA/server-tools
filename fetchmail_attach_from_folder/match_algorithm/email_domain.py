# Copyright - 2013-2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from .email_exact import EmailExact


class EmailDomain(EmailExact):
    """Search objects by domain name of email address.

    Beware of match_first here, this is most likely to get it wrong (gmail).
    """

    def search_matches(self, folder, message_dict):
        """Returns recordset of matching objects."""
        matches = super().search_matches(folder, message_dict)
        if not matches:
            object_model = folder.env[folder.model_id.model]
            domains = []
            for addr in self._get_mailaddresses(folder, message_dict):
                domains.append(addr.split("@")[-1])
            matches = object_model.search(
                self._get_mailaddress_search_domain(
                    folder,
                    message_dict,
                    operator="like",
                    values=["%@" + domain for domain in set(domains)],
                ),
                order=folder.model_order,
            )
        return matches
