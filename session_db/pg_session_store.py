# Copyright (c) Odoo SA 2017
# @author Nicolas Seinlet
# Copyright (c) ACSONE SA 2022
# @author Stéphane Bidoul
import json
import logging
import os

import psycopg2

import odoo
from odoo import http
from odoo.tools._vendor import sessions
from odoo.tools.func import lazy_property

_logger = logging.getLogger(__name__)

lock = None
if odoo.evented:
    import gevent.lock

    lock = gevent.lock.RLock()
elif odoo.tools.config["workers"] == 0:
    import threading

    lock = threading.RLock()


def with_lock(func):
    def wrapper(*args, **kwargs):
        try:
            if lock is not None:
                lock.acquire()
            return func(*args, **kwargs)
        finally:
            if lock is not None:
                lock.release()

    return wrapper


def with_cursor(func):
    def wrapper(self, *args, **kwargs):
        tries = 0
        while True:
            tries += 1
            try:
                self._ensure_connection()
                return func(self, *args, **kwargs)
            except (psycopg2.InterfaceError, psycopg2.OperationalError):
                self._close_connection()
                if tries > 4:
                    _logger.warning(
                        "session_db operation try %s/5 failed, aborting", tries
                    )
                    raise
                _logger.info("session_db operation try %s/5 failed, retrying", tries)

    return wrapper


class PGSessionStore(sessions.SessionStore):
    def __init__(self, uri, session_class=None):
        super().__init__(session_class)
        self._uri = uri
        self._cr = None
        self._open_connection()
        self._setup_db()

    def __del__(self):
        self._close_connection()

    @with_lock
    def _ensure_connection(self):
        if self._cr is None:
            self._open_connection()

    @with_lock
    def _open_connection(self):
        self._close_connection()
        cnx = odoo.sql_db.db_connect(self._uri, allow_uri=True)
        self._cr = cnx.cursor()
        self._cr._cnx.autocommit = True

    @with_lock
    def _close_connection(self):
        """Return cursor to the pool."""
        if self._cr is not None:
            try:
                self._cr.close()
            except Exception:  # pylint: disable=except-pass
                pass
            self._cr = None

    @with_lock
    @with_cursor
    def _setup_db(self):
        self._cr.execute(
            """
                CREATE TABLE IF NOT EXISTS http_sessions (
                    sid varchar PRIMARY KEY,
                    write_date timestamp without time zone NOT NULL,
                    payload text NOT NULL
                )
            """
        )

    @with_lock
    @with_cursor
    def save(self, session):
        payload = json.dumps(dict(session))
        self._cr.execute(
            """
                INSERT INTO http_sessions(sid, write_date, payload)
                    VALUES (%(sid)s, now() at time zone 'UTC', %(payload)s)
                ON CONFLICT (sid)
                DO UPDATE SET payload = %(payload)s,
                              write_date = now() at time zone 'UTC'
            """,
            dict(sid=session.sid, payload=payload),
        )

    @with_lock
    @with_cursor
    def delete(self, session):
        self._cr.execute("DELETE FROM http_sessions WHERE sid=%s", (session.sid,))

    @with_lock
    @with_cursor
    def get(self, sid):
        self._cr.execute("SELECT payload FROM http_sessions WHERE sid=%s", (sid,))
        try:
            data = json.loads(self._cr.fetchone()[0])
        except Exception:
            return self.new()

        return self.session_class(data, sid, False)

    # This method is not part of the Session interface but is called nevertheless,
    # so let's get it from FilesystemSessionStore.
    rotate = http.FilesystemSessionStore.rotate

    @with_lock
    @with_cursor
    def vacuum(self, max_lifetime=http.SESSION_LIFETIME):
        self._cr.execute(
            "DELETE FROM http_sessions "
            "WHERE now() at time zone 'UTC' - write_date > %s",
            (f"{max_lifetime} seconds",),
        )


_original_session_store = http.root.__class__.session_store


@lazy_property
def session_store(self):
    session_db_uri = os.environ.get("SESSION_DB_URI")
    if session_db_uri:
        _logger.debug("HTTP sessions stored in: db")
        return PGSessionStore(session_db_uri, session_class=http.Session)
    return _original_session_store.__get__(self, self.__class__)


# Monkey patch of standard methods
_logger.debug("Monkey patching session store")
http.root.__class__.session_store = session_store
# Reset the lazy property cache
vars(http.root).pop("session_store", None)
