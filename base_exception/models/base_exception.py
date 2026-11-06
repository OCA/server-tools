# Copyright 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# Copyright 2017 Akretion (http://www.akretion.com)
# Copyright 2025 Raumschmiede GmbH
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
    exceptions_summary = fields.Html(
        "Exceptions Summary", compute="_compute_exceptions_summary"
    )
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

    @api.depends(
        "exception_ids",
        "exception_ids.name",
        "exception_ids.description",
        "exception_ids.description_text_type",
        "exception_ids.is_blocking",
        "ignore_exception",
    )
    def _compute_exceptions_summary(self):
        for rec in self:
            if rec.exception_ids and not rec.ignore_exception:
                rec.exceptions_summary = rec._get_exceptions_summary()
            else:
                rec.exceptions_summary = False

    def _get_exceptions_summary(self):
        self.ensure_one()

        summaries = []
        for exception in self.exception_ids:
            summaries += self._get_exceptions_summaries_by_exception(exception)

        return self._get_pretty_exceptions_summary_from_summaries(summaries)

    def _get_exceptions_summaries_by_exception(self, exception):
        self.ensure_one()

        # True if the description is e.g. empty or flagged as plain description. We
        # expect that no record is used to render the description, that's why self can
        # be used to get the description. Even if exception.model is not self._name
        if not exception.description_needs_rendering():
            return [self._get_pretty_summary_for_exception(exception)]

        # If the exception needs to be rendered, we have to get the records on which
        # the exception was detected on to use them for rendering. If the exception
        # model is self._name or the exception was detected on a sub-record whose model
        # inherits from base.exception.method, records will the same as self.
        records = self._get_records_for_description_rendering(exception)

        summaries = []
        for record in records:
            # Even with rendering it can happen that multiple records return the same
            # rendered description, e.g. if the description is plain text but its type
            # is set to Jinja. The same description will be added multiple times to the
            # final summary. With that the user knows that multiple sub-records have
            # the same exception assigned and were rendered
            summary = record._get_pretty_summary_for_exception(exception)
            summaries.append(summary)

        return summaries

    def _get_records_for_description_rendering(self, exception):
        self.ensure_one()

        if exception.model == self._name:
            # Exception needs the current record to render
            return self

        sub_record_ids = []
        # Collect all sub-records that have the exception
        for field in self._get_sub_exception_field_names():
            sub_records = self.mapped(field)

            if exception.model != sub_records._name:
                continue

            for sub_record in sub_records:
                # For models that inherit from base.exception.method this is always
                # False. Only for base.exception models it can be True
                if sub_record._has_exception_rule_assigned(exception):
                    sub_record_ids.append(sub_record.id)

        if sub_record_ids:
            return self.env[exception.model].browse(sub_record_ids)

        # If there are no sub-records that have the exception assigned, possible
        # because their model inherits from base.exception.method, self is returned
        # to use it to render the description. This means it is not possible to
        # use the same model in the description syntax as the model on which the
        # exception was detected on
        return self

    def _get_pretty_summary_for_exception(self, exception):
        self.ensure_one()

        args = list(
            map(
                html.escape,
                (
                    exception.name,
                    exception.render_description(self),
                ),
            )
        )

        if exception.is_blocking:
            args.append(_(" <b>(Blocking exception)</b>"))
        else:
            args.append("")

        return "%s: <i>%s</i>%s" % tuple(args)

    def _get_pretty_exceptions_summary_from_summaries(self, summaries):
        return "<ul>%s</ul>" % "".join(
            map(lambda summary: f"<li>{summary}</li>", summaries)
        )

    def _popup_exceptions(self):
        action = self._get_popup_action().sudo().read()[0]
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

    def _add_detected_exceptions_to_self(self):
        return self != self._get_main_records()

    def _has_exception_rule_assigned(self, exception):
        # Models inheriting from base.exception have exception_ids as field. Records of
        # this model can be checked to have exceptions. Because of this the record can
        # be used to render the exception description
        return exception in self.exception_ids

    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        # If _get_main_records returns self, it adds the exceptions to itself in
        # detect_exceptions. If _get_main_records does not return self, it adds the
        # exceptions here
        if not self._add_detected_exceptions_to_self():
            return records

        (self - records).exception_ids = [(3, rule.id)]
        records.exception_ids = [(4, rule.id)]

        return records

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
