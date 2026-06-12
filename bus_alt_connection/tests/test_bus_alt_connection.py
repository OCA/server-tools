# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import threading
from unittest import mock

from odoo.tests.common import TransactionCase

from ..models import bus as bus_alt


class _FakeNotify:
    def __init__(self, payload):
        self.payload = payload


class _FakeCursor:
    def __init__(self):
        self.execute = mock.Mock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeConnection:
    def __init__(self, notifies=None):
        self._cursor = _FakeCursor()
        self.commit = mock.Mock()
        self.poll = mock.Mock()
        self.notifies = list(notifies or [])

    def cursor(self):
        return self._cursor


class _FakeSelector:
    def __init__(self, select_returns=None, on_select=None):
        self._select_returns = list(select_returns or [])
        self._on_select = on_select
        self.register = mock.Mock()
        self.select_calls = 0

    def select(self, timeout=None):
        self.select_calls += 1
        if self._on_select:
            self._on_select(timeout)
        if self._select_returns:
            return self._select_returns.pop(0)
        return []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TestBusAltConnection(TransactionCase):
    def test01_connection_info_config_overrides(self):
        with mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.odoo.sql_db.connection_info_for"
        ) as connection_info_for, mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.config.get"
        ) as config_get:
            connection_info_for.return_value = (
                None,
                {
                    "host": "pgbouncer",
                    "port": 6432,
                    "database": "postgres",
                    "user": "odoo",
                },
            )
            config_get.side_effect = lambda key: {
                "imdispatcher_db_host": "direct-db",
                "imdispatcher_db_port": 5432,
            }.get(key)
            info = bus_alt._connection_info_for("postgres")
        assert info["host"] == "direct-db"
        assert info["port"] == 5432
        assert info["database"] == "postgres"

    def test02_connection_info_env_takes_precedence(self):
        with mock.patch.dict(
            bus_alt.os.environ,
            {
                "ODOO_IMDISPATCHER_DB_HOST": "env-db",
                "ODOO_IMDISPATCHER_DB_PORT": "15432",
            },
            clear=False,
        ), mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.odoo.sql_db.connection_info_for"
        ) as connection_info_for, mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.config.get"
        ) as config_get:
            connection_info_for.return_value = (
                None,
                {
                    "host": "pgbouncer",
                    "port": 6432,
                    "database": "postgres",
                    "user": "odoo",
                },
            )
            config_get.side_effect = lambda key: {
                "imdispatcher_db_host": "direct-db",
                "imdispatcher_db_port": 5432,
            }.get(key)
            info = bus_alt._connection_info_for("postgres")
        assert info["host"] == "env-db"
        # env vars come as strings
        assert info["port"] == "15432"

    def test03_connection_info_no_override_keeps_original(self):
        with mock.patch.dict(
            bus_alt.os.environ,
            {
                "ODOO_IMDISPATCHER_DB_HOST": "",
                "ODOO_IMDISPATCHER_DB_PORT": "",
            },
            clear=False,
        ), mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.odoo.sql_db.connection_info_for"
        ) as connection_info_for, mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.config.get"
        ) as config_get:
            connection_info_for.return_value = (
                None,
                {
                    "host": "pgbouncer",
                    "port": 6432,
                    "database": "postgres",
                    "user": "odoo",
                },
            )
            config_get.return_value = None
            info = bus_alt._connection_info_for("postgres")
        assert info["host"] == "pgbouncer"
        assert info["port"] == 6432

    def test04_loop_dispatches_unique_websockets(self):
        stop_event = threading.Event()
        ws1 = mock.Mock()
        ws2 = mock.Mock()
        channel_1 = ("db", "ch1")
        channel_2 = ("db", "ch2")
        notifies = [
            _FakeNotify('[["db", "ch1"]]'),
            _FakeNotify('[["db", "ch1"], ["db", "ch2"]]'),
        ]
        fake_conn = _FakeConnection(notifies=notifies)
        fake_selector = _FakeSelector(
            select_returns=[[object()]],
            on_select=lambda _timeout: stop_event.set(),
        )
        dispatch = bus_alt.ImDispatch()
        dispatch._channels_to_ws = {
            bus_alt.hashable(channel_1): [ws1],
            bus_alt.hashable(channel_2): [ws1, ws2],
        }
        with mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.stop_event", stop_event
        ), mock.patch(
            "odoo.addons.bus_alt_connection.models.bus._connection_info_for"
        ) as connection_info_for, mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.psycopg2.connect"
        ) as connect, mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.selectors.DefaultSelector"
        ) as DefaultSelector:
            connection_info_for.return_value = {"host": "h", "port": 1}
            connect.return_value = fake_conn
            DefaultSelector.return_value = fake_selector

            dispatch.loop()

        fake_conn._cursor.execute.assert_called_once_with("listen imbus")
        fake_conn.commit.assert_called_once()
        fake_conn.poll.assert_called_once()
        ws1.trigger_notification_dispatching.assert_called_once()
        ws2.trigger_notification_dispatching.assert_called_once()

    def test05_loop_no_activity_does_not_poll(self):
        stop_event = threading.Event()
        fake_conn = _FakeConnection(notifies=[])
        fake_selector = _FakeSelector(
            select_returns=[[]],
            on_select=lambda _timeout: stop_event.set(),
        )
        dispatch = bus_alt.ImDispatch()
        dispatch._channels_to_ws = {}
        with mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.stop_event", stop_event
        ), mock.patch(
            "odoo.addons.bus_alt_connection.models.bus._connection_info_for"
        ) as connection_info_for, mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.psycopg2.connect"
        ) as connect, mock.patch(
            "odoo.addons.bus_alt_connection.models.bus.selectors.DefaultSelector"
        ) as DefaultSelector:
            connection_info_for.return_value = {"host": "h", "port": 1}
            connect.return_value = fake_conn
            DefaultSelector.return_value = fake_selector
            dispatch.loop()
        fake_conn.poll.assert_not_called()
