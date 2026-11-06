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
        self.uri = _make_postgres_uri(**connection_info)
        self.session_store = PGSessionStore(self.uri, session_class=http.Session)

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

    def test_logout_survives_a_stale_save(self):
        """A session read before logout and saved after it stays deleted"""
        session = self.session_store.new()
        session["uid"] = self.env.uid
        self.session_store.save(session)
        sid = session.sid
        # e.g. the bus websocket handshake, running while the user logs out
        stale = self.session_store.get(sid)
        self.session_store.delete(session)
        self.session_store.save(stale)
        self.assertEqual(stale.sid, sid)
        restored = self.session_store.get(sid)
        self.assertNotEqual(restored.sid, sid)
        self.assertIsNone(restored.get("uid"))

    def test_anonymous_save_on_deleted_sid_gets_a_new_sid(self):
        session = self.session_store.new()
        session["test"] = "test"
        self.session_store.save(session)
        sid = session.sid
        self.session_store.delete(session)
        self.session_store.save(session)
        self.assertNotEqual(session.sid, sid)
        self.assertEqual(self.session_store.get(session.sid)["test"], "test")
        self.assertIsNone(self.session_store.get(sid).get("test"))

    def test_upgrade_table_without_deleted_column(self):
        """A table created by an earlier version is upgraded, keeping its rows"""
        cursor = self.session_store._cr
        session = self.session_store.new()
        session["test"] = "test"
        try:
            cursor.execute("ALTER TABLE http_sessions DROP COLUMN deleted")
            cursor.execute(
                "INSERT INTO http_sessions(sid, write_date, payload) "
                "VALUES (%s, now() at time zone 'UTC', %s)",
                (session.sid, '{"test": "test"}'),
            )
        finally:
            session_store = PGSessionStore(self.uri, session_class=http.Session)
        sid = session.sid
        self.assertEqual(session_store.get(sid)["test"], "test")
        session_store.delete(session)
        session_store.save(session)
        self.assertNotEqual(session.sid, sid)
        self.assertIsNone(session_store.get(sid).get("test"))
