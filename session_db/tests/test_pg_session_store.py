import logging
import time
from unittest import mock

import psycopg2

from odoo import http
from odoo.sql_db import connection_info_for
from odoo.tests import TransactionCase
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
        _, connection_info = connection_info_for(config["db_name"][0])
        self.uri = _make_postgres_uri(**connection_info)
        self.session_store = PGSessionStore(self.uri, session_class=http.Session)

    def _new_user_session(self):
        session = self.session_store.new()
        session.update(uid=self.env.uid, create_time=time.time())
        self.session_store.save(session)
        return session

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
            except RuntimeError as e:  # pylint: disable=except-pass
                assert str(e) == "connection failed"
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

    def test_get_missing_session_identifiers(self):
        session1 = self.session_store.new()
        session2 = self.session_store.new()
        self.session_store.save(session1)
        self.session_store.save(session2)
        missing = self.session_store.get_missing_session_identifiers(
            [session1.sid[:42], session2.sid[:42], "nonexistentsessionid"]
        )
        self.assertEqual(missing, {"nonexistentsessionid"})
        self.session_store.delete(session1)
        missing = self.session_store.get_missing_session_identifiers(
            [session1.sid[:42], session2.sid[:42], "nonexistentsessionid"]
        )
        self.assertEqual(missing, {session1.sid[:42], "nonexistentsessionid"})

    def test_delete_from_identifiers(self):
        session1 = self.session_store.new()
        session2 = self.session_store.new()
        self.session_store.save(session1)
        self.session_store.save(session2)
        self.session_store.delete_from_identifiers([session1.sid[:42], "f" * 42])
        self.assertNotEqual(self.session_store.get(session1.sid).sid, session1.sid)
        self.assertEqual(self.session_store.get(session2.sid).sid, session2.sid)

    def test_delete_from_identifiers_invalid_format(self):
        with self.assertRaises(ValueError):
            self.session_store.delete_from_identifiers("xxx")

    def test_logout_survives_a_stale_save(self):
        """A session read before logout and saved after it stays deleted"""
        session = self._new_user_session()
        sid = session.sid
        # e.g. the bus websocket handshake, running while the user logs out
        stale = self.session_store.get(sid)
        self.session_store.delete(session)
        self.session_store.save(stale)
        self.assertEqual(stale.sid, sid)
        restored = self.session_store.get(sid)
        self.assertNotEqual(restored.sid, sid)
        self.assertIsNone(restored.get("uid"))
        self.assertEqual(
            self.session_store.get_missing_session_identifiers([sid[:42]]),
            {sid[:42]},
        )

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

    def test_soft_rotation_after_logout(self):
        """A stale request that soft-rotates the session cannot log it back in"""
        session = self._new_user_session()
        sid = session.sid
        stale = self.session_store.get(sid)
        self.session_store.delete(session)
        self.session_store.rotate(stale, self.env, soft=True)
        self.assertNotEqual(stale.sid, sid)
        self.assertNotEqual(self.session_store.get(stale.sid).sid, stale.sid)

    def test_soft_rotation(self):
        session = self._new_user_session()
        self.session_store.rotate(session, self.env, soft=True)
        self.assertEqual(self.session_store.get(session.sid)["uid"], self.env.uid)

    def test_upgrade_table_without_deleted_column(self):
        """A table created by an earlier version is upgraded, keeping its rows"""
        cursor = self.session_store._cursor
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
