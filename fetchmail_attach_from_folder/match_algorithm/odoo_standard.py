# Copyright - 2013-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from .base import Base


class OdooStandard(Base):
    """No search at all. Use Odoo's standard mechanism to attach mails to
    mail.thread objects. Note that this algorithm always matches."""

    name = "Odoo standard"
    readonly_fields = [
        "model_field",
        "mail_field",
        "match_first",
        "domain",
        "model_order",
        "flag_nonmatching",
    ]

    def search_matches(self, folder, mail_message):
        """Always match. Duplicates will be fished out by message_id"""
        return [True]

    def handle_match(
        self, connection, match_object, folder, mail_message, mail_message_org, msgid
    ):
        thread_model = folder.env["mail.thread"]
        thread_model.message_process(
            folder.model_id.model,
            mail_message_org,
            save_original=folder.server_id.original,
            strip_attachments=(not folder.server_id.attach),
        )
