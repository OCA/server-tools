# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.http import request
from odoo.service import security

logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    def _get_partner_name(self, user_id):
        return self.env["res.users"].browse(user_id).partner_id.name

    def _is_impersonate_user(self):
        self.ensure_one()
        return self.has_group("impersonate_login.group_impersonate_login")

    def impersonate_login(self):
        if request:
            if request.session.impersonate_from_uid:
                raise UserError(_("You are already Logged as another user."))
            if self.id == request.session.uid:
                raise UserError(_("It's you."))
            if request.env.user._is_impersonate_user():
                target_uid = self.id
                request.session.impersonate_from_uid = self._uid
                request.session.uid = target_uid
                impersonate_log = (
                    self.env["impersonate.log"]
                    .sudo()
                    .create(
                        {
                            "user_id": self.env["res.users"]
                            .browse(self._uid)
                            .partner_id.id,
                            "impersonated_user_id": self.env["res.users"]
                            .browse(target_uid)
                            .partner_id.id,
                            "date_start": fields.datetime.now(),
                        }
                    )
                )
                request.session.impersonate_log_id = impersonate_log.id
                logger.info(
                    f"IMPERSONATE: {self._get_partner_name(self._uid)} "
                    f"Login as {self._get_partner_name(self.id)}"
                )

                request.env["res.users"].clear_caches()
                request.session.session_token = security.compute_session_token(
                    request.session, request.env
                )
                return {
                    "type": "ir.actions.client",
                    "tag": "reload",
                }

    @api.model
    def back_to_origin_login(self):
        if request:
            from_uid = request.session.impersonate_from_uid
            if from_uid:
                request.session.uid = from_uid
                self.env["impersonate.log"].sudo().browse(
                    request.session.impersonate_log_id
                ).write(
                    {
                        "date_end": fields.datetime.now(),
                    }
                )
                request.env["res.users"].clear_caches()
                request.session.impersonate_from_uid = False
                request.session.impersonate_log_id = False
                request.session.session_token = security.compute_session_token(
                    request.session, request.env
                )
                logger.info(
                    f"IMPERSONATE: {self._get_partner_name(from_uid)} "
                    f"Logout as {self._get_partner_name(self._uid)}"
                )
