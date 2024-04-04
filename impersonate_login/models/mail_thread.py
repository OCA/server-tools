# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.http import request


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_compute_author(
        self, author_id=None, email_from=None, raise_exception=True
    ):
        if (
            request
            and request.session.impersonate_from_uid
            and author_id in [request.session.uid, None]
        ):
            author = (
                self.env["res.users"]
                .browse(request.session.impersonate_from_uid)
                .partner_id
            )
            email = author.email_formatted
            return author.id, email
        else:
            return super()._message_compute_author(
                author_id, email_from, raise_exception
            )
