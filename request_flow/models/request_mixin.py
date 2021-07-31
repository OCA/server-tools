# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RequestDocMixin(models.AbstractModel):
    _name = "request.doc.mixin"
    _description = "Child doc of the request"

    # Child Documents are freezed, if request is in these states
    _request_freeze_states = []
    # Child Documents can move to this approved state, only when request is approved
    _doc_approved_states = []

    ref_request_id = fields.Many2one(
        comodel_name="request.request",
        index=True,
        ondelete="restrict",
        copy=False,
    )

    def write(self, vals):
        for rec in self.filtered("ref_request_id"):
            # Affect from _request_freeze_states
            if rec.ref_request_id.state in self._request_freeze_states:
                raise ValidationError(
                    _(
                        "This document is part of %s which is under validation.\n"
                        "No changes allowed!"
                    )
                    % rec.ref_request_id.display_name
                )
            # Affect from _doc_states_by_request
            if self._doc_approved_states and rec.ref_request_id.state != "approved":
                if vals.get("state") in self._doc_approved_states:
                    raise ValidationError(
                        _("This action will be approved when Request %s is approved.")
                        % rec.ref_request_id.display_name
                    )
        return super().write(vals)

    @api.onchange("ref_request_id")
    def _onchange_ref_request_set_defaults(self):
        if self.ref_request_id:
            vals = self._prepare_defaults()
            self.update(vals)

    def _prepare_defaults(self):
        """ Hook method to prepare default for creating doc """
        return {}

    def action_open_request(self):
        self.ensure_one()
        action = {
            "name": _("Requests"),
            "view_mode": "form",
            "res_model": "request.request",
            "res_id": self.ref_request_id.id,
            "type": "ir.actions.act_window",
            "context": self.env.context,
        }
        return action

    @api.constrains("state")
    def _trigger_ready_to_submit(self):
        for request in self.sudo().filtered("ref_request_id").mapped("ref_request_id"):
            # Update only when changed, to minimize trigger to request
            if request.ready_to_submit != request._ready_to_submit():
                request.ready_to_submit = request._ready_to_submit()
            # If child document has made request ready, create activity to warn requester
            request._mail_act_ready_to_submit()

    def _run_doc_action(self, action_type, alt_model=False):
        self.ensure_one()
        child_doc_option = self.ref_request_id.category_id.child_doc_option_ids
        model = alt_model or self._name
        doc_option = child_doc_option.filtered_domain([("model", "=", model)])[:1]
        ctx = self.env.context.copy()
        ctx.update(
            {
                "active_model": self._name,
                "active_id": self.id,
            }
        )
        if action_type == "approved":
            doc_option.approved_action_id.with_context(ctx).sudo().run()
        if action_type == "rejected":
            doc_option.rejected_action_id.with_context(ctx).sudo().run()


class RequestDocLineMixin(models.AbstractModel):
    _name = "request.doc.line.mixin"
    _description = "Child doc line of the request"

    ref_request_id = fields.Many2one(
        comodel_name="request.request",
        copy=False,
    )

    @api.onchange("ref_request_id")
    def _onchange_ref_request_set_defaults(self):
        if self.ref_request_id:
            vals = self._prepare_defaults()
            self.update(vals)

    def _prepare_defaults(self):
        """ Hook method to prepare default for creating doc line """
        return {}
