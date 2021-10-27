# Copyright 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# Copyright 2020 Hibou Corp.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import html

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class ExceptionRule(models.Model):
    _name = "exception.rule"
    _description = "Exception Rule"
    _order = "active desc, sequence asc"

    name = fields.Char("Exception Name", required=True, translate=True)
    description = fields.Text("Description", translate=True)
    sequence = fields.Integer(
        string="Sequence", help="Gives the sequence order when applying the test"
    )
    model = fields.Selection(selection=[], string="Apply on", required=True)

    exception_type = fields.Selection(
        selection=[("by_domain", "By domain"), ("by_py_code", "By python code")],
        string="Exception Type",
        required=True,
        default="by_py_code",
        help="By python code: allow to define any arbitrary check\n"
        "By domain: limited to a selection by an odoo domain:\n"
        "           performance can be better when exceptions "
        "           are evaluated with several records",
    )
    domain = fields.Char("Domain")

    active = fields.Boolean("Active", default=True)
    code = fields.Text(
        "Python Code",
        help="Python code executed to check if the exception apply or "
        "not. Use failed = True to block the exception",
    )

    @api.constrains("exception_type", "domain", "code")
    def check_exception_type_consistency(self):
        for rule in self:
            if (rule.exception_type == "by_py_code" and not rule.code) or (
                rule.exception_type == "by_domain" and not rule.domain
            ):
                raise ValidationError(
                    _(
                        "There is a problem of configuration, python code or "
                        "domain is missing to match the exception type."
                    )
                )

    def _get_domain(self):
        """ override me to customize domains according exceptions cases """
        self.ensure_one()
        return safe_eval(self.domain)


class BaseExceptionMethod(models.AbstractModel):
    _name = "base.exception.method"
    _description = "Exception Rule Methods"

    def _get_main_records(self):
        """
        Used in case we check exceptions on a record but write these
        exceptions on a parent record. Typical example is with
        sale.order.line. We check exceptions on some sale order lines but
        write these exceptions on the sale order, so they are visible.
        """
        return self

    def _reverse_field(self):
        raise NotImplementedError()

    def _rule_domain(self):
        """Filter exception.rules.
        By default, only the rules with the correct model
        will be used.
        """
        return [("model", "=", self._name)]

    def detect_exceptions(self):
        """List all exception_ids applied on self
        Exception ids are also written on records
        """
        rules = self.env["exception.rule"].sudo().search(self._rule_domain())
        all_exception_ids = []
        rules_to_remove = {}
        rules_to_add = {}
        for rule in rules:
            records_with_exception = self._detect_exceptions(rule)
            reverse_field = self._reverse_field()
            main_records = self._get_main_records()
            commons = main_records & rule[reverse_field]
            to_remove = commons - records_with_exception
            to_add = records_with_exception - commons
            # we expect to always work on the same model type
            if rule.id not in rules_to_remove:
                rules_to_remove[rule.id] = main_records.browse()
            rules_to_remove[rule.id] |= to_remove
            if rule.id not in rules_to_add:
                rules_to_add[rule.id] = main_records.browse()
            rules_to_add[rule.id] |= to_add
            if records_with_exception:
                all_exception_ids.append(rule.id)
        # Cumulate all the records to attach to the rule
        # before linking. We don't want to call "rule.write()"
        # which would:
        # * write on write_date so lock the exception.rule
        # * trigger the recomputation of "main_exception_id" on
        #   all the sale orders related to the rule, locking them all
        #   and preventing concurrent writes
        # Reversing the write by writing on SaleOrder instead of
        # ExceptionRule fixes the 2 kinds of unexpected locks.
        # It should not result in more queries than writing on ExceptionRule:
        # the "to remove" part generates one DELETE per rule on the relation
        # table
        # and the "to add" part generates one INSERT (with unnest) per rule.
        for rule_id, records in rules_to_remove.items():
            records.write({"exception_ids": [(3, rule_id)]})
        for rule_id, records in rules_to_add.items():
            records.write({"exception_ids": [(4, rule_id)]})
        return all_exception_ids

    @api.model
    def _exception_rule_eval_context(self, rec):
        return {
            "self": rec,
            "object": rec,
            "obj": rec,
        }

    @api.model
    def _rule_eval(self, rule, rec):
        expr = rule.code
        space = self._exception_rule_eval_context(rec)
        try:
            safe_eval(
                expr, space, mode="exec", nocopy=True
            )  # nocopy allows to return 'result'
        except Exception as e:
            raise UserError(
                _("Error when evaluating the exception.rule rule:\n %s \n(%s)")
                % (rule.name, e)
            )
        return space.get("failed", False)

    def _detect_exceptions(self, rule):
        if rule.exception_type == "by_py_code":
            return self._detect_exceptions_by_py_code(rule)
        elif rule.exception_type == "by_domain":
            return self._detect_exceptions_by_domain(rule)

    def _get_base_domain(self):
        return [("ignore_exception", "=", False), ("id", "in", self.ids)]

    def _detect_exceptions_by_py_code(self, rule):
        """
        Find exceptions found on self.
        """
        domain = self._get_base_domain()
        records = self.search(domain)
        records_with_exception = self.env[self._name]
        for record in records:
            if self._rule_eval(rule, record):
                records_with_exception |= record
        return records_with_exception

    def _detect_exceptions_by_domain(self, rule):
        """
        Find exceptions found on self.
        """
        base_domain = self._get_base_domain()
        rule_domain = rule._get_domain()
        domain = expression.AND([base_domain, rule_domain])
        return self.search(domain)


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
                        "<li>%s: <i>%s</i></li>"
                        % tuple(map(html.escape, (e.name, e.description or "")))
                        for e in rec.exception_ids
                    ]
                )
            else:
                rec.exceptions_summary = False

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
