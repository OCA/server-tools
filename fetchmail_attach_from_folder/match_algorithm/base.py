# -*- coding: utf-8 -*-
# Copyright - 2013-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


class Base(object):
    name = None  # Name shown to the user

    # Fields on fetchmail_server folder required for this algorithm
    required_fields = []

    # Fields on fetchmail_server folder readonly for this algorithm
    readonly_fields = []

    def search_matches(self, folder, mail_message):
        """Returns recordset found for model with mail_message."""
        return []

    def handle_match(
            self, connection, match_object, folder,
            mail_message, mail_message_org, msgid):
        """Do whatever it takes to handle a match"""
        folder.attach_mail(match_object, mail_message)
