from unittest import mock

import base64
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
        """Tests that binary data (bytes) converts to a string with a prefix
        when saving, and converts back to bytes when reading.
        """
        original_data = {
            "normal_text": "test",
            "binary_data": b"Test binary",
        }

        # 1. Simulate save (session_to_str)
        serialized = self.session_store.session_to_str(original_data)
        # Verify that the prefix was added and encoded in base64
        expected_b64 = base64.b64encode(b"Test binary").decode("utf-8")
        self.assertEqual(
            serialized["binary_data"],
            f"base64::{expected_b64}",
            "Binary data should be serialized with the base64:: prefix"
        )
        self.assertEqual(serialized["normal_text"], "test")

        # 2. Simulate read (str_to_session)
        deserialized = self.session_store.str_to_session(serialized)
        # Verify that we recover the 'bytes' type
        self.assertEqual(deserialized["binary_data"], b"Test binary")
        self.assertIsInstance(deserialized["binary_data"], bytes)

    def test_numeric_conversion(self):
        """Tests that strings looking like numbers convert to int/float."""
        data_from_json = {
            "integer_str": "42",
            "float_str": "3.1416",
            "negative_int": "-10",
            "negative_float": "-0.01",
            "plain_text": "123-abc"  # Should not convert
        }
        result = self.session_store.str_to_session(data_from_json)
        # Integer validations
        self.assertEqual(result["integer_str"], 42)
        self.assertIsInstance(result["integer_str"], int)
        self.assertEqual(result["negative_int"], -10)
        # Float validations
        self.assertEqual(result["float_str"], 3.1416)
        self.assertIsInstance(result["float_str"], float)
        self.assertEqual(result["negative_float"], -0.01)
        # Text validations that must not change
        self.assertEqual(result["plain_text"], "123-abc")
        self.assertIsInstance(result["plain_text"], str)

    def test_debug_param_exception(self):
        """Verifies that the "debug" key ALWAYS remains a string,
        even if it looks like an integer ("1").
        """
        data = {
            "debug": "1",  # Special case: must remain string
            "assets_debug": "1",  # Normal case: must be int
            "debug_nested": {"debug": "0"}  # Recursive test
        }
        result = self.session_store.str_to_session(data)

        # "debug" must be string "1", NOT integer 1
        self.assertEqual(result["debug"], "1")
        self.assertIsInstance(result["debug"], str)
        # Other keys do convert
        self.assertEqual(result["assets_debug"], 1)
        self.assertIsInstance(result["assets_debug"], int)
        # Verify exception applies recursively if the key is "debug"
        self.assertEqual(result["debug_nested"]["debug"], "0")
        self.assertIsInstance(result["debug_nested"]["debug"], str)

    def test_recursive_traversal(self):
        """Tests that conversion works in nested structures (lists and dicts).
        """
        data = {
            "list_of_data": [
                b"binary_in_list",
                "100",
                {"deep_key": "50.5"}
            ]
        }
        # 1. Serialize (Bytes -> Str)
        serialized = self.session_store.session_to_str(data)
        self.assertTrue(serialized["list_of_data"][0].startswith("base64::"))
        # 2. Deserialize (Str -> Bytes/Int/Float)
        # Simulate that JSON already loaded the string "100" and "50.5"
        # Note: session_to_str does not convert ints to strings, json.dumps does that later.
        # Here we test str_to_session with data appearing to come from JSON.
        input_for_read = {
            "list_of_data": [
                serialized["list_of_data"][0],  # The base64 string
                "100",
                {"deep_key": "50.5"}
            ]
        }
        result = self.session_store.str_to_session(input_for_read)

        self.assertEqual(result["list_of_data"][0], b"binary_in_list")
        self.assertEqual(result["list_of_data"][1], 100)
        self.assertEqual(result["list_of_data"][2]["deep_key"], 50.5)

    def test_invalid_base64_fallback(self):
        """If a string has the base64:: prefix but the content is invalid,
        it must return the original value without crashing.
        """
        invalid_data = {
            "bad_binary": "base64::THIS_IS_NOT_VALID_BASE64"
        }
        result = self.session_store.str_to_session(invalid_data)
        # Should return the original string intact
        self.assertEqual(result["bad_binary"], "base64::THIS_IS_NOT_VALID_BASE64")
