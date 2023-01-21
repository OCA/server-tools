# -*- coding: utf-8 -*-
# Copyright (c) Odoo SA 2017
# @author Nicolas Seinlet
# Copyright (c) ACSONE SA 2022
# @author Stéphane Bidoul
import json
import logging
import os
import random
import time

import psycopg2
import werkzeug.contrib.sessions

import odoo
from odoo import http
from odoo.tools.func import lazy_property

_logger = logging.getLogger(__name__)


def with_cursor(func):
    def wrapper(self, *args, **kwargs):
        tries = 0
        while True:
            tries += 1
            try:
                return func(self, *args, **kwargs)
            except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
                _logger.info("Session in DB connection Retry %s/5" % tries)
                if tries > 4:
                    raise e
                self._open_connection()

    return wrapper


class PGSessionStore(werkzeug.contrib.sessions.SessionStore):
    def __init__(self, uri, session_class=None):
        super(PGSessionStore, self).__init__(session_class)
        self._uri = uri
        self._cr = None
        # FIXME This class is NOT thread-safe. Only use in worker mode
        if odoo.tools.config["workers"] == 0:
            raise ValueError("session_db requires multiple workers")
        self._open_connection()
        self._setup_db()

    def __del__(self):
        if self._cr is not None:
            self._cr.close()

    def _open_connection(self):
        cnx = odoo.sql_db.db_connect(self._uri, allow_uri=True)
        try:
            # return cursor to the pool
            if self._cr is not None:
                self._cr.close()
                self._cr = None
        except Exception:
            pass
        self._cr = cnx.cursor()
        self._cr.autocommit(True)

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

    @with_cursor
    def delete(self, session):
        self._cr.execute("DELETE FROM http_sessions WHERE sid=%s", (session.sid,))

    @with_cursor
    def get(self, sid):
        self._cr.execute("SELECT payload FROM http_sessions WHERE sid=%s", (sid,))
        try:
            payload, = self._cr.fetchone()
            data = json.loads(payload)
            session_token = data.get('session_token')
            if session_token:
                # the session token is compared to the one in the session cookie
                # the one into the cookie is encoded into utf-8. To avoid
                # encoding issues in the call to odoo.tools.misc.consteq, we
                # encode the one from the database into utf-8 too.
                data["session_token"] = session_token.encode('utf-8')
        except Exception:
            return self.new()

        return self.session_class(data, sid, False)

    @with_cursor
    def gc(self):
        self._cr.execute(
            "DELETE FROM http_sessions "
            "WHERE now() at time zone 'UTC' - write_date > '7 days'"
        )


def session_gc(session_store):
    """
    Global cleaning of sessions using either the standard way (delete session files),
    Or the DB way.
    """
    if random.random() < 0.001:
        # we keep session one week
        if hasattr(session_store, "gc"):
            session_store.gc()
            return
        last_week = time.time() - 60 * 60 * 24 * 7
        for fname in os.listdir(session_store.path):
            path = os.path.join(session_store.path, fname)
            try:
                if os.path.getmtime(path) < last_week:
                    os.unlink(path)
            except OSError:
                pass


_original_session_store = http.root.__class__.session_store


@lazy_property
def session_store(self):
    session_db_uri = os.environ.get("SESSION_DB_URI")
    if session_db_uri:
        _logger.debug("HTTP sessions stored in: db")
        return PGSessionStore(session_db_uri, session_class=http.OpenERPSession)
    return _original_session_store.__get__(self, self.__class__)


# Monkey patch of standard methods
_logger.debug("Monkey patching session store")
http.session_gc = session_gc
http.root.__class__.session_store = session_store
# Reset the lazy property cache
vars(http.root).pop("session_store", None)
