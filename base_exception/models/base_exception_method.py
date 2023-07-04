# Copyright 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# Copyright 2020 Hibou Corp.
# Copyright 2023 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


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

    def _rule_domain(self):
        """Filter exception.rules.
        By default, only the rules with the correct model
        will be used.
        """
        return [("model", "=", self._name), ("active", "=", True)]

    def detect_exceptions(self):
        """List all exception_ids applied on self
        Exception ids are also written on records
        """
        rules = self.env["exception.rule"].sudo().search(self._rule_domain())
        all_exception_ids = []
        rules_to_remove = {}
        rules_to_add = {}
        for rule in rules:
            main_records = self._get_main_records()
            records_with_rule_in_exceptions = main_records.filtered(
                lambda r, rule_id=rule.id: rule_id in r.exception_ids.ids
            )
            records_with_exception = self._detect_exceptions(rule)
            to_remove = records_with_rule_in_exceptions - records_with_exception
            to_add = records_with_exception - records_with_rule_in_exceptions
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
            _logger.exception(e)
            raise UserError(
                _(
                    "Error when evaluating the exception.rule"
                    " rule:\n %(rule_name)s \n(%(error)s)"
                )
                % {"rule_name": rule.name, "error": e}
            ) from e
        return space.get("failed", False)

    def _detect_exceptions(self, rule):
        if rule.exception_type == "by_py_code":
            return self._detect_exceptions_by_py_code(rule)
        elif rule.exception_type == "by_domain":
            return self._detect_exceptions_by_domain(rule)
        elif rule.exception_type == "by_method":
            return self._detect_exceptions_by_method(rule)

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

    def _detect_exceptions_by_method(self, rule):
        """
        Find exceptions found on self.
        """
        base_domain = self._get_base_domain()
        records = self.search(base_domain)
        return getattr(records, rule.method)()
