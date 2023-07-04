# Copyright 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# Copyright 2020 Hibou Corp.
# Copyright 2023 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import html
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BaseExceptionModel(models.AbstractModel):
    _inherit = "base.exception.method"
    _name = "base.exception"
    _order = "main_exception_id asc"
    _description = "Exception"

    main_exception_id = fields.Many2one(
        "exception.rule",
        compute="_compute_main_error",
        string="Main Exception",
        store=True,
    )
    exceptions_summary = fields.Html(compute="_compute_exceptions_summary")
    exception_ids = fields.Many2many("exception.rule", string="Exceptions", copy=False)
    ignore_exception = fields.Boolean("Ignore Exceptions", copy=False)

    def action_ignore_exceptions(self):
        if any(self.exception_ids.mapped("is_blocking")):
            raise UserError(
                _(
                    "The exceptions can not be ignored, because "
                    "some of them are blocking."
                )
            )
        self.write({"ignore_exception": True})
        return True

    @api.depends("exception_ids", "ignore_exception")
    def _compute_main_error(self):
        for rec in self:
            if not rec.ignore_exception and rec.exception_ids:
                rec.main_exception_id = rec.exception_ids[0]
            else:
                rec.main_exception_id = False

    @api.depends("exception_ids", "ignore_exception")
    def _compute_exceptions_summary(self):
        for rec in self:
            if rec.exception_ids and not rec.ignore_exception:
                rec.exceptions_summary = "<ul>%s</ul>" % "".join(
                    [
                        "<li>%s: <i>%s</i> <b>%s<b></li>"
                        % tuple(
                            map(
                                html.escape,
                                (
                                    e.name,
                                    e.description or "",
                                    _("(Blocking exception)") if e.is_blocking else "",
                                ),
                            )
                        )
                        for e in rec.exception_ids
                    ]
                )
            else:
                rec.exceptions_summary = False

    def _popup_exceptions(self):
        """This method is used to show the popup action view.
        Used in several dependent modules."""
        record = self._get_popup_action()
        action = record.sudo().read()[0]
        action = {
            field: value
            for field, value in action.items()
            if field in record._get_readable_fields()
        }
        action.update(
            {
                "context": {
                    "active_id": self.ids[0],
                    "active_ids": self.ids,
                    "active_model": self._name,
                }
            }
        )
        return action

    @api.model
    def _get_popup_action(self):
        return self.env.ref("base_exception.action_exception_rule_confirm")

    def _check_exception(self):
        """Check exceptions

        This method must be used in a constraint that must be created in the
        object that inherits for base.exception.

        .. code-block:: python

            @api.constrains("ignore_exception")
            def sale_check_exception(self):
                # ...
                self._check_exception()

        For convenience, this check can be skipped by setting check_exception=False
        in context.

        Exceptions will be raised as ValidationError, but this can be disabled
        by setting raise_exception=False in context. They will still be detected
        and updated on the related record, though.
        """
        if not self.env.context.get("check_exception", True):  # pragma: no cover
            return True
        exception_ids = self.detect_exceptions()
        if exception_ids and self.env.context.get("raise_exception", True):
            exceptions = self.env["exception.rule"].browse(exception_ids)
            raise ValidationError("\n".join(exceptions.mapped("name")))
