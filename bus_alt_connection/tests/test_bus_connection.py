import json
import os
import selectors
from unittest.mock import MagicMock, call, patch

from odoo.tests import common
from odoo.tools import config

from odoo.addons.bus_alt_connection.models.bus import ImDispatch, _connection_info_for

stop_event = MagicMock(name="stop_event")
TIMEOUT = 5.0


def hashable(x):
    return tuple(x) if isinstance(x, list) else x


class TestImDispatchOverride(common.TransactionCase):
    TEST_DB_NAME = "postgres"

    @patch("odoo.sql_db.connection_info_for")
    def test_01_connection_info_for_default(self, mock_info_for):
        mock_info_for.return_value = (
            self.TEST_DB_NAME,
            {"user": "odoo_user", "password": "pwd", "host": "127.0.0.1", "port": 5432},
        )
        with (
            patch.dict(os.environ, clear=True),
            patch.object(config, "get", return_value=None),
        ):
            info = _connection_info_for(self.TEST_DB_NAME)
            self.assertEqual(info["host"], "127.0.0.1")
            self.assertEqual(info["port"], 5432)
            self.assertEqual(info["user"], "odoo_user")

    @patch("odoo.sql_db.connection_info_for")
    @patch.dict(
        os.environ,
        {
            "ODOO_IMDISPATCHER_DB_HOST": "db_host_env",
            "ODOO_IMDISPATCHER_DB_PORT": "6000",
        },
        clear=True,
    )
    def test_02_connection_info_for_env_override(self, mock_info_for):
        mock_info_for.return_value = (
            self.TEST_DB_NAME,
            {"host": "127.0.0.1", "port": 5432, "user": "odoo_user"},
        )
        with patch.object(config, "get", return_value=None):
            info = _connection_info_for(self.TEST_DB_NAME)
            self.assertEqual(
                info["host"], "db_host_env", "Debe usar ODOO_IMDISPATCHER_DB_HOST"
            )
            self.assertEqual(
                info["port"], "6000", "Debe usar ODOO_IMDISPATCHER_DB_PORT"
            )
            self.assertEqual(
                info["user"], "odoo_user", "Otros parámetros deben permanecer iguales"
            )

    @patch("odoo.sql_db.connection_info_for")
    @patch.dict(os.environ, clear=True)
    def test_03_connection_info_for_config_override(self, mock_info_for):
        """Prueba que se sobrescribe con la configuración de Odoo (odoo.conf)."""

        mock_info_for.return_value = (
            self.TEST_DB_NAME,
            {"host": "127.0.0.1", "port": 5432},
        )

        def mock_config_get(key):
            return {
                "imdispatcher_db_host": "db_host_config",
                "imdispatcher_db_port": "5433",
            }.get(key)

        with patch.object(
            config, "get", side_effect=mock_config_get
        ) as mock_config_get_patch:
            info = _connection_info_for(self.TEST_DB_NAME)

            self.assertEqual(
                info["host"], "db_host_config", "Debe usar imdispatcher_db_host"
            )
            self.assertEqual(info["port"], "5433", "Debe usar imdispatcher_db_port")

            self.assertIn(
                call("imdispatcher_db_host"), mock_config_get_patch.call_args_list
            )
            self.assertIn(
                call("imdispatcher_db_port"), mock_config_get_patch.call_args_list
            )

    @patch(
        "odoo.addons.bus_alt_connection.models.bus.selectors"
    )  # 1º Arg: mock_selectors
    @patch(
        "odoo.addons.bus_alt_connection.models.bus.psycopg2"
    )  # 2º Arg: mock_psycopg2
    @patch(
        "odoo.addons.bus_alt_connection.models.bus.stop_event"
    )  # 3º Arg: mock_stop_event
    @patch("odoo.addons.bus_alt_connection.models.bus._logger")  # 4º Arg: mock_logger
    def test_04_loop_dispatches_notifications(
        self, mock_selectors, mock_psycopg2, mock_stop_event, mock_logger
    ):
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        MockNotification = MagicMock
        mock_conn.notifies = [
            MockNotification(payload=json.dumps(["c1"])),
            MockNotification(payload=json.dumps(["c2"])),
        ]
        mock_selector = MagicMock(spec=selectors.DefaultSelector)
        mock_selectors.DefaultSelector.return_value.__enter__.return_value = (
            mock_selector
        )
        mock_selector.select.side_effect = [[(MagicMock(), selectors.EVENT_READ)], []]
        mock_stop_event.is_set.side_effect = [
            False,  # Primera vuelta: Ejecutar
            True,  # Segunda vuelta: Detener
        ]
        dispatcher = ImDispatch()
        ws_c1 = MagicMock(name="ws_c1")
        ws_c2 = MagicMock(name="ws_c2")
        ws_unrelated = MagicMock(name="ws_unrelated")
        dispatcher._channels_to_ws = {
            hashable(["c1"]): [ws_c1],
            hashable(["c2"]): [ws_c2],
            hashable(["c3"]): [ws_unrelated],
        }
        dispatcher.loop()
