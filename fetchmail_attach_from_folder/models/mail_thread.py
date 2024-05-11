# Copyright - 2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, models

from .. import match_algorithm

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_route(
        self,
        message,
        message_dict,
        model=None,
        thread_id=None,
        custom_values=None,
    ):
        """Override to apply matching algorithm to determine thread_id if requested."""
        if not thread_id and custom_values and "folder" in custom_values:
            match = self._find_match(custom_values, message_dict)
            if not match:
                return []  # This will ultimately return thread_id = False
            thread_id = match.id
        return super().message_route(
            message,
            message_dict,
            model=model,
            thread_id=thread_id,
            custom_values=custom_values,
        )

    @api.model
    def _find_match(self, custom_values, message_dict):
        """Try to find existing object to link mail to."""
        folder = custom_values.pop("folder")
        matcher = self._get_algorithm(folder.match_algorithm)
        if not matcher:
            return None
        matches = matcher.search_matches(folder, message_dict)
        if not matches:
            _logger.info(
                "No match found for message %(subject)s with msgid %(msgid)s",
                {
                    "subject": message_dict.get("subject", "no subject"),
                    "msgid": message_dict.get("message_id", "no msgid"),
                },
            )
            return None
        matched = len(matches) == 1 or folder.match_first
        return matched and matches[0] or None

    @api.model
    def _get_algorithm(self, algorithm):
        """Translate algorithm code to implementation class.

        We used to load this dynamically, but having it more or less hardcoded
        allows to adapt the UI to the selected algorithm, withouth needing
        the (deprecated) fields_view_get trickery we used in the past.
        """
        if algorithm == "email_domain":
            return match_algorithm.email_domain.EmailDomain()
        if algorithm == "email_exact":
            return match_algorithm.email_exact.EmailExact()
        _logger.error("Unknown algorithm %(algorithm)s", {"algorithm": algorithm})
        return None
