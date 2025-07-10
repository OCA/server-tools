# Copyright (c) Odoo SA 2017
# @author Nicolas Seinlet
# Copyright (c) ACSONE SA 2022
# @author Stéphane Bidoul
import base64
import json
import logging
import os
import re

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
        self.prefix_binary = "base64::"

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
        json_session = self.session_to_str(dict(session))
        payload = json.dumps(json_session)
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
            data = self.str_to_session(data)
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

    def _traverse_and_convert(self, data_node, conversion_func):
        """Helper method that preserves keys while converting values."""
        if isinstance(data_node, dict):
            res = {}
            for key, value in data_node.items():
                # This is necessary because Odoo's core (ir_qweb) needs the 'debug' value as
                # a string.
                # The value for this key can be: "1", "assets", "True", "False", etc.
                # Ref: https://github.com/Vauxoo/odoo/blob/d4d64d613800b8dc44c3262e13a2a81dbf3c742c/
                # odoo/addons/base/models/ir_qweb.py#L912
                # A test on an Odoo instance without the 'session_db' module confirmed
                # that 'request.session.debug' value is always a string (str) type.
                if key != "debug":
                    key = self._traverse_and_convert(key, conversion_func)
                    value = self._traverse_and_convert(value, conversion_func)
                res.update({key: value})
            return res
        if isinstance(data_node, list):
            return [
                self._traverse_and_convert(item, conversion_func) for item in data_node
            ]
        return conversion_func(data_node)

    def session_to_str(self, data):
        """Converts binary values to prefixed strings."""

        def convert(value):
            if isinstance(value, bytes):
                base64_string = base64.b64encode(value).decode("utf-8")
                return self.prefix_binary + base64_string
            return value

        return self._traverse_and_convert(data, convert)

    def str_to_session(self, data):
        """Converts binary str to binary value again.
        Converts int/float str values convert to their respective types.
        """

        def convert(value):
            if not isinstance(value, str):
                return value  # Only process strings
            # 1. Check for binary
            if value.startswith(self.prefix_binary):
                base64_string = value[len(self.prefix_binary) :]
                try:
                    return base64.b64decode(base64_string)
                except (ValueError, TypeError):
                    pass
            numeric_parsers = [
                # 2. Check for float (positive or negative)
                # This regex requires a decimal point.
                (r"^-?\d+\.\d+$", float),
                # 3. Check for integer (positive or negative)
                # This regex matches only digits (with optional sign).
                (r"^-?\d+$", int),
            ]
            for pattern, parser in numeric_parsers:
                if re.match(pattern, value):
                    try:
                        return parser(value)
                    except (ValueError, TypeError):
                        pass
            return value

        return self._traverse_and_convert(data, convert)


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
