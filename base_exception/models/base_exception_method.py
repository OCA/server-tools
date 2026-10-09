# Copyright 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# Copyright 2020 Hibou Corp.
# Copyright 2023 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import json
import logging
from collections import defaultdict

from psycopg2.errors import LockNotAvailable

from odoo import Command, _, api, models
from odoo.api import Environment
from odoo.exceptions import MissingError, UserError
from odoo.osv import expression
from odoo.tools import config, mute_logger
from odoo.tools.safe_eval import safe_eval

from ..exceptions import BaseExceptionError

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

    def _get_exceptions(self):
        """
        Returns a tuple with:
        - All exceptions
        - Rules to remove with recordset
        - Rules to add with recordset
        """
        rules_info = (
            self.env["exception.rule"]
            .sudo()
            ._get_rules_info_for_domain(self._rule_domain())
        )
        all_exception_ids = []
        main_records = self._get_main_records()
        rules_to_remove = defaultdict(main_records.browse)
        rules_to_add = defaultdict(main_records.browse)
        for rule_info in rules_info:
            records_with_rule_in_exceptions = main_records.filtered(
                lambda r, rule_id=rule_info.id: rule_id in r.exception_ids.ids
            )
            records_with_exception = self._detect_exceptions(rule_info)
            to_remove = records_with_rule_in_exceptions - records_with_exception
            to_add = records_with_exception - records_with_rule_in_exceptions
            if to_remove:
                rules_to_remove[rule_info.id] |= to_remove
            if to_add:
                rules_to_add[rule_info.id] |= to_add
            if records_with_exception:
                all_exception_ids.append(rule_info.id)
        return all_exception_ids, rules_to_remove, rules_to_add

    def detect_exceptions(self):
        """List all exception_ids applied on self
        Exception ids are also written on records
        """
        all_exception_ids, rules_to_remove, rules_to_add = self._get_exceptions()
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
        raise_exception = False
        # The registry is not ready yet when modules are being installed or
        # updated: the ongoing transaction holds exclusive locks on the tables
        # it has just modified (ALTER TABLE ...), so any query made through a
        # second connection would wait forever on those locks (and the locks
        # cannot be released, as the current thread is the one waiting).
        # Use the current cursor in that case, as already done when running
        # tests.
        test_mode = (
            config["test_enable"] or not self.env.registry.ready
        ) and not self.env.context.get("test_base_exception")
        # Resolve the main records (e.g. the sale order behind a sale order
        # line) using the current cursor, which sees records created earlier
        # in this same transaction even before they are committed.
        main_records = self._get_main_records()

        def write_exceptions(env):
            for rule_id, records in rules_to_remove.items():
                records.with_env(env).write(
                    {"exception_ids": [Command.unlink(rule_id)]}
                )
            for rule_id, records in rules_to_add.items():
                records.with_env(env).write({"exception_ids": [Command.link(rule_id)]})

        # Write exceptions in a new transaction to be committed so that we can
        #  rollback the ongoing one while keeping the exceptions stored
        with self.env.registry.cursor() as new_cr:
            new_env = (
                Environment(new_cr, self.env.uid, self.env.context)
                if not test_mode
                else self.env
            )
            write_env = self._write_exceptions_independently(new_env, write_exceptions)
            # In case we have new exception, or exceptions that were not ignored yet, or
            #  blocking exceptions, we need to raise an exception to rollback the
            #  ongoing transaction.
            # Re-derive main_records through write_env rather than re-running
            # self.with_env(write_env)._get_main_records(): when self are
            # records just created earlier in the ongoing (not yet committed)
            # transaction (e.g. a line added while editing a confirmed sale
            # order), new_cr is a genuinely separate DB connection that
            # cannot see them yet, and _get_main_records() traversal
            # (e.g. sale.order.line -> order_id) would raise MissingError.
            # main_records itself was already resolved above through the
            # current cursor, so only rebinding it to write_env is needed here.
            main_records_new_env = main_records.with_env(write_env)
            if (
                rules_to_add
                or main_records_new_env._must_raise_exception_after_detection()
            ):
                raise_exception = True
        if raise_exception:
            raise BaseExceptionError(
                json.dumps(self._detect_exception_get_exc_class_values())
            )
        return all_exception_ids

    def _get_exception_lock_timeout(self):
        """Milliseconds the independent transaction waits for a row lock
        before giving up on writing the exceptions on its own."""
        return 2000

    def _write_exceptions_independently(self, new_env, write_func):
        """Call ``write_func(env)`` to write exception data through
        ``new_env``, whose independent transaction is committed so the data
        survives a rollback of the ongoing one.

        The ongoing transaction may already hold locks on the rows to write
        (e.g. an order line it has just written). The independent
        transaction would then wait for the ongoing one, which is itself
        waiting for this method to return: PostgreSQL cannot detect that
        deadlock and the request would hang forever. So the independent
        transaction only waits ``_get_exception_lock_timeout()``.

        The records may also have been created by the ongoing transaction
        (e.g. a line added to a confirmed order), which the independent
        transaction cannot see yet.

        In both cases the data is written in the ongoing transaction, so
        the exceptions are still detected and raised, and written again in
        a new transaction if the ongoing one is rolled back, once its locks
        are released.

        :return: the environment the data was written with
        """
        if new_env is self.env:
            write_func(new_env)
            return new_env
        try:
            with mute_logger("odoo.sql_db"), new_env.cr.savepoint():
                new_env.cr.execute(
                    "SET LOCAL lock_timeout = %s",
                    (self._get_exception_lock_timeout(),),
                )
                write_func(new_env)
        except (LockNotAvailable, MissingError) as error:
            _logger.info(
                "Exceptions of %s are written in the ongoing transaction, and "
                "again if it is rolled back, as the independent one failed: %s",
                self,
                error,
            )
        else:
            return new_env
        write_func(self.env)
        registry = self.env.registry
        uid = self.env.uid
        context = dict(self.env.context)

        @self.env.cr.postrollback.add
        def write_exceptions_after_rollback():
            # An error here would break closing the rolled back cursor.
            try:
                with registry.cursor() as cr:
                    write_func(Environment(cr, uid, context))
            except MissingError:
                _logger.debug(
                    "Records created by the rolled back transaction, no "
                    "exceptions to write"
                )
            except Exception as error:
                _logger.warning(
                    "Exceptions could not be written after a rollback: %s", error
                )

        return self.env

    def _detect_exception_get_exc_class_values(self):
        return {
            "src_model": self._name,
            "target_model": self._name,
        }

    def _must_raise_exception_after_detection(self):
        main_records = self._get_main_records()
        all_ignore_exception = all(
            main_records.filtered("exception_ids").mapped("ignore_exception")
        )
        any_blocking_exception = any(
            rule.is_blocking for rule in main_records.exception_ids
        )
        return not all_ignore_exception or any_blocking_exception

    @api.model
    def _exception_rule_eval_context(self, rec):
        return {
            "self": rec,
            "object": rec,
            "obj": rec,
        }

    @api.model
    def _rule_eval(self, rule_info, rec):
        expr = rule_info.code
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
                % {"rule_name": rule_info.name, "error": e}
            ) from e
        return space.get("failed", False)

    def _detect_exceptions(self, rule_info):
        if rule_info.exception_type == "by_py_code":
            return self._detect_exceptions_by_py_code(rule_info)
        elif rule_info.exception_type == "by_domain":
            return self._detect_exceptions_by_domain(rule_info)
        elif rule_info.exception_type == "by_method":
            return self._detect_exceptions_by_method(rule_info)

    def _get_base_domain(self):
        return [("ignore_exception", "=", False)]

    def _detect_exceptions_by_py_code(self, rule_info):
        """
        Find exceptions found on self.
        """
        domain = self._get_base_domain()
        records = self.filtered_domain(domain)
        records_with_exception = self.env[self._name]
        for record in records:
            if self._rule_eval(rule_info, record):
                records_with_exception |= record
        return records_with_exception

    def _detect_exceptions_by_domain(self, rule_info):
        """
        Find exceptions found on self.
        """
        base_domain = self._get_base_domain()
        rule_domain = rule_info.domain
        domain = expression.AND([base_domain, rule_domain])
        return self.filtered_domain(domain)

    def _detect_exceptions_by_method(self, rule_info):
        """
        Find exceptions found on self.
        """
        base_domain = self._get_base_domain()
        records = self.filtered_domain(base_domain)
        return getattr(records, rule_info.method)()
