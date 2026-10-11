# Copyright (C) 2026 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import UserError


def _is_clickhouse_readonly_mode(env):
    """Check whether auditlog is currently in ClickHouse-backed read-only mode.

    Read-only mode is considered enabled when auditlog records are read through
    PostgreSQL FDW relations backed by ClickHouse.

    :param odoo.api.Environment env: Current Odoo environment.
    :return: ``True`` if auditlog read mode is ``"fdw"``, otherwise ``False``.
    :rtype: bool
    """
    return env["auditlog.clickhouse.config"].sudo()._get_auditlog_read_mode() == "fdw"


def _raise_clickhouse_readonly(env):
    """Raise a user-facing error for auditlog read-only mode.

    This helper is used to block any write operation on auditlog models while
    ClickHouse FDW read mode is enabled.

    :param odoo.api.Environment env: Current Odoo environment.
    :raises UserError: Always, with a message explaining that audit logs are
        read-only while FDW read mode is enabled.
    """
    raise UserError(env._("Audit logs are read-only while FDW read mode is enabled."))


class AuditlogLogReadonly(models.Model):
    """Prevent modifications of ``auditlog.log`` in FDW read mode."""

    _inherit = "auditlog.log"

    @api.model_create_multi
    def create(self, vals_list):
        """Block creation of auditlog log records in FDW read mode.

        :param list[dict] vals_list: Values for records to create.
        :return: Created records from the parent implementation.
        :rtype: odoo.models.Model
        :raises UserError: If auditlog is currently in ClickHouse read-only mode.
        """
        if _is_clickhouse_readonly_mode(self.env):
            _raise_clickhouse_readonly(self.env)
        return super().create(vals_list)

    def write(self, vals):
        """Block updates of auditlog log records in FDW read mode.

        :param dict vals: Values to write on the recordset.
        :return: Result of the parent ``write`` call.
        :rtype: bool
        :raises UserError: If auditlog is currently in ClickHouse read-only mode.
        """
        if _is_clickhouse_readonly_mode(self.env):
            _raise_clickhouse_readonly(self.env)
        return super().write(vals)

    def unlink(self):
        """Block deletion of auditlog log records in FDW read mode.

        :return: Result of the parent ``unlink`` call.
        :rtype: bool
        :raises UserError: If auditlog is currently in ClickHouse read-only mode.
        """
        if _is_clickhouse_readonly_mode(self.env):
            _raise_clickhouse_readonly(self.env)
        return super().unlink()


class AuditlogLogLineReadonly(models.Model):
    """Prevent modifications of ``auditlog.log.line`` in FDW read mode."""

    _inherit = "auditlog.log.line"

    @api.model_create_multi
    def create(self, vals_list):
        """Block creation of auditlog log line records in FDW read mode.

        :param list[dict] vals_list: Values for records to create.
        :return: Created records from the parent implementation.
        :rtype: odoo.models.Model
        :raises UserError: If auditlog is currently in ClickHouse read-only mode.
        """
        if _is_clickhouse_readonly_mode(self.env):
            _raise_clickhouse_readonly(self.env)
        return super().create(vals_list)

    def write(self, vals):
        """Block updates of auditlog log line records in FDW read mode.

        :param dict vals: Values to write on the recordset.
        :return: Result of the parent ``write`` call.
        :rtype: bool
        :raises UserError: If auditlog is currently in ClickHouse read-only mode.
        """
        if _is_clickhouse_readonly_mode(self.env):
            _raise_clickhouse_readonly(self.env)
        return super().write(vals)

    def unlink(self):
        """Block deletion of auditlog log line records in FDW read mode.

        :return: Result of the parent ``unlink`` call.
        :rtype: bool
        :raises UserError: If auditlog is currently in ClickHouse read-only mode.
        """
        if _is_clickhouse_readonly_mode(self.env):
            _raise_clickhouse_readonly(self.env)
        return super().unlink()
