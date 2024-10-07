import logging
from unittest import mock

import psycopg2

from odoo import http
from odoo.sql_db import connection_info_for
from odoo.tests.common import TransactionCase
from odoo.tools import config

from odoo.addons.session_db.pg_session_store import PGSessionStore


def _make_postgres_uri(
    login=None, password=None, host=None, port=None, database=None, **kwargs
):
    uri = ["postgres://"]
    if login:
        uri.append(login)
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
        with (
            mock.patch("odoo.sql_db.Cursor.execute") as mock_execute,
            self.assertLogs(level=logging.WARNING) as logs,
        ):
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
            self.assertEqual(len(logs.records), 1)
            self.assertEqual(logs.records[0].levelno, logging.WARNING)
            self.assertIn("operation try 5/5 failed, aborting", logs.output[0])
        # when the error is resolved, it works again
        self.session_store.get("abc")

    def test_retry_connect_fail(self):
        with (
            mock.patch("odoo.sql_db.Cursor.execute") as mock_execute,
            mock.patch("odoo.sql_db.db_connect") as mock_db_connect,
        ):
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
