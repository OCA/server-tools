# Copyright (C) 2026 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class AuditlogClickhouseReadCommon(BaseCommon):
    """Shared test helpers for ``auditlog_clickhouse_read`` test cases.

    The class provides:

    - a test environment with tracking disabled;
    - access to the ``auditlog.clickhouse.config`` model;
    - cleanup helpers to reset configuration state between test suites;
    - a factory method for creating test ClickHouse configurations.
    """

    @classmethod
    def setUpClass(cls):
        """Prepare shared test state for read-module test classes.

        The method:

        - disables tracking in the test environment;
        - caches the configuration model on ``cls.Config``;
        - resets previously created ClickHouse read test data.
        """
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Config = cls.env["auditlog.clickhouse.config"].with_context(
            tracking_disable=True
        )
        cls._cleanup_read_test_data()

    @classmethod
    def tearDownClass(cls):
        """Clean up shared ClickHouse read test data after the test class.

        The cleanup is executed in a ``try/finally`` block to ensure that the
        base class teardown still runs even if local cleanup fails.
        """
        try:
            cls._cleanup_read_test_data()
        finally:
            super().tearDownClass()

    @classmethod
    def _cleanup_read_test_data(cls):
        """Reset ClickHouse configuration state created by read-module tests.

        All existing ``auditlog.clickhouse.config`` records are forced into a
        neutral state so test cases do not influence each other through active
        or FDW-enabled configurations.
        """
        configs = (
            cls.env["auditlog.clickhouse.config"]
            .sudo()
            .with_context(tracking_disable=True)
            .search([])
        )
        if configs:
            configs.write({"fdw_enabled": False, "is_active": False})

    @classmethod
    def create_config(cls, **vals):
        """Create a ClickHouse configuration record with test defaults.

        Default values are sufficient for most unit tests and can be overridden
        through keyword arguments.

        :param dict vals: Field values overriding the default configuration.
        :return: Newly created ClickHouse configuration record.
        :rtype: odoo.models.Model
        """
        defaults = {
            "host": "127.0.0.1",
            "port": 9000,
            "database": "db",
            "user": "default",
            "password": "123",
            "is_active": False,
        }
        defaults.update(vals)
        return cls.Config.create(defaults)
