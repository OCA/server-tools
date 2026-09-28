import base64
from unittest import mock

import psycopg2

from odoo import http
from odoo.sql_db import connection_info_for
from odoo.tests.common import TransactionCase
from odoo.tools import config

from odoo.addons.session_db.pg_session_store import PGSessionStore


def _make_postgres_uri(
    user=None, password=None, host=None, port=None, database=None, **kwargs
):
    uri = ["postgres://"]
    if user:
        uri.append(user)
        if password:
            uri.append(f":{password}")
        uri.append("@")
    if host:
        uri.append(host)
        if port:
            uri.append(f":{port}")
    uri.append("/")
    if database:
        uri.append(database)
    return "".join(uri)


class TestPGSessionStore(TransactionCase):
    def setUp(self):
        super().setUp()
        _, connection_info = connection_info_for(config["db_name"])
        self.session_store = PGSessionStore(
            _make_postgres_uri(**connection_info), session_class=http.Session
        )

    def test_session_crud(self):
        session = self.session_store.new()
        session["test"] = "test"
        self.session_store.save(session)
        assert session.sid is not None
        assert self.session_store.get(session.sid)["test"] == "test"
        self.session_store.delete(session)
        assert self.session_store.get(session.sid).get("test") is None

    def test_retry(self):
        """Test that session operations are retried before failing"""
        with mock.patch("odoo.sql_db.Cursor.execute") as mock_execute:
            mock_execute.side_effect = psycopg2.OperationalError()
            try:
                self.session_store.get("abc")
            except psycopg2.OperationalError:  # pylint: disable=except-pass
                pass
            else:
                # We don't use self.assertRaises because Odoo is overriding
                # in a way that interferes with the Cursor.execute mock
                raise AssertionError("expected psycopg2.OperationalError")
            assert mock_execute.call_count == 5
        # when the error is resolved, it works again
        self.session_store.get("abc")

    def test_retry_connect_fail(self):
        with mock.patch("odoo.sql_db.Cursor.execute") as mock_execute, mock.patch(
            "odoo.sql_db.db_connect"
        ) as mock_db_connect:
            mock_execute.side_effect = psycopg2.OperationalError()
            mock_db_connect.side_effect = RuntimeError("connection failed")
            # get fails, and a RuntimeError is raised when trying to reconnect
            try:
                self.session_store.get("abc")
            except RuntimeError:  # pylint: disable=except-pass
                pass
            else:
                # We don't use self.assertRaises because Odoo is overriding
                # in a way that interferes with the Cursor.execute mock
                raise AssertionError("expected RuntimeError")
            assert mock_execute.call_count == 1
        # when the error is resolved, it works again
        self.session_store.get("abc")

    def test_make_postgres_uri(self):
        connection_info = {
            "host": "localhost",
            "port": 5432,
            "database": "test",
            "user": "test",
            "password": "PASSWORD",
        }
        assert "postgres://test:PASSWORD@localhost:5432/test" == _make_postgres_uri(
            **connection_info
        )

    def test_binary_serialization_roundtrip(self):
        """Ensures binary data is safely serialized to a base64 string
        and accurately deserialized back to bytes."""
        original_data = {
            "normal_text": "test",
            "binary_data": b"Test binary",
        }
        serialized = self.session_store.session_to_str(original_data)
        expected_b64 = base64.b64encode(b"Test binary").decode("utf-8")
        self.assertEqual(
            serialized["binary_data"],
            f"base64::{expected_b64}",
            "Binary data should be serialized with the configured prefix.",
        )
        self.assertEqual(serialized["normal_text"], "test")

        deserialized = self.session_store.str_to_session(serialized)
        self.assertEqual(deserialized["binary_data"], b"Test binary")
        self.assertIsInstance(deserialized["binary_data"], bytes)

    def test_recursive_traversal(self):
        """Verifies that base64 serialization works inside nested structures."""
        data = {
            "list_of_data": [b"binary_in_list", "100", {"deep_key": b"deep_binary"}]
        }
        serialized = self.session_store.session_to_str(data)
        self.assertTrue(serialized["list_of_data"][0].startswith("base64::"))
        self.assertTrue(
            serialized["list_of_data"][2]["deep_key"].startswith("base64::")
        )

        result = self.session_store.str_to_session(serialized)
        self.assertEqual(result["list_of_data"][0], b"binary_in_list")
        self.assertEqual(result["list_of_data"][1], "100")
        self.assertEqual(result["list_of_data"][2]["deep_key"], b"deep_binary")

    def test_invalid_base64_fallback(self):
        """Failsafe: Invalid base64 strings with the exact prefix must return
        the original string without crashing the session load."""
        invalid_data = {"bad_binary": "base64::TESTS_INVALID_@#$"}
        result = self.session_store.str_to_session(invalid_data)
        self.assertEqual(result["bad_binary"], "base64::TESTS_INVALID_@#$")
