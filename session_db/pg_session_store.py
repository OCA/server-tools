# Copyright (c) Odoo SA 2017
# @author Nicolas Seinlet
# Copyright (c) ACSONE SA 2022
# @author Stéphane Bidoul
import contextlib
import hashlib
import hmac
import json
import logging
import os
import tempfile
import time

import psycopg2

import odoo
from odoo.http import session as http_session
from odoo.tools import SQL
from odoo.tools.misc import consteq

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


class PGSessionStore(http_session.SessionStore):
    def __init__(self, /, path=None, session_cls=http_session.Session, *, uri=None):
        super().__init__(path=path, session_cls=session_cls)
        self._uri = uri or os.environ["SESSION_DB_URI"]
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
            with contextlib.suppress(Exception):
                self._cr.close()
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
            {"sid": session.sid, "payload": payload},
        )

    @with_lock
    @with_cursor
    def delete(self, session):
        self._cr.execute("DELETE FROM http_sessions WHERE sid=%s", (session.sid,))

    @with_lock
    @with_cursor
    def get(self, sid, *, keep_sid=False):
        if not self.is_valid_session_id(sid):
            return self.new()
        self._cr.execute("SELECT payload FROM http_sessions WHERE sid=%s", (sid,))
        row = self._cr.fetchone()
        if row is None:
            if keep_sid:
                return self.session_cls({}, sid, new=False)
            return self.new()
        try:
            data = json.loads(row[0])
        except ValueError:
            # The session exists in the database (the sid must be retained)
            data = {}
        return self.session_cls(data, sid, new=False)

    @with_lock
    @with_cursor
    def get_many(self, sids):
        """Return the stored sessions keyed by sid, leaving out the missing ones."""
        self._cr.execute(
            "SELECT sid, payload FROM http_sessions WHERE sid = ANY(%s)", (list(sids),)
        )
        sessions = {}
        for sid, payload in self._cr.fetchall():
            try:
                data = json.loads(payload)
            except ValueError:
                data = {}
            sessions[sid] = self.session_cls(data, sid, new=False)
        return sessions

    @with_lock
    @with_cursor
    def vacuum(self, max_lifetime=http_session.SESSION_LIFETIME):
        self._cr.execute(
            "DELETE FROM http_sessions "
            "WHERE now() at time zone 'UTC' - write_date > %s",
            (f"{max_lifetime} seconds",),
        )

    @with_lock
    @with_cursor
    def get_missing_session_identifiers(self, identifiers: list[str]) -> set[str]:
        """
        :param identifiers: session identifiers whose file existence must be checked
                            identifiers are a part session sid (first 42 chars)
        :type identifiers: iterable
        :return: the identifiers which are not present on the filesystem
        :rtype: set

        Note 1:
        Working with identifiers 42 characters long means that
        we don't have to work with the entire sid session,
        while maintaining sufficient entropy to avoid collisions.
        See details in ``generate_key``.

        Note 2:
        Scans the session store for inactive (GC'd) sessions.
        Performance is acceptable for an infrequent background job.
        """
        missing_identifiers = set()
        for identifier in identifiers:
            self._cr.execute(
                "SELECT sid FROM http_sessions WHERE sid LIKE %s||'%%' LIMIT 1",
                (identifier,),
            )
            if self._cr.rowcount == 0:
                missing_identifiers.add(identifier)
        return missing_identifiers

    @with_lock
    @with_cursor
    def delete_from_identifiers(self, identifiers: list[str]) -> None:
        for identifier in identifiers:
            if not http_session._session_identifier_re.match(identifier):
                raise ValueError(
                    "Identifier format incorrect, "
                    "did you pass in a string instead of a list?"
                )
            self._cr.execute(
                "DELETE FROM http_sessions WHERE sid LIKE %s||'%%'", (identifier,)
            )


def check_sessions(cr, sessions):
    """Replacement of ``odoo.addons.bus.session_helpers.check_sessions``.

    The original opens the session file to know if the session still exists, so with
    this store it would treat every logged-in websocket as expired. This version asks
    the store instead, with one query for all the sessions; the rest of the checks
    are the same.
    """
    store = http_session.session_store()
    now = time.time()
    resolved_by_sid = {}
    to_check_by_sid = {}
    sessions = list(sessions)
    stored_by_sid = store.get_many({s.sid for s in sessions if s.uid is not None})
    for stored_session in sessions:
        if (
            stored_session.sid in resolved_by_sid
            or stored_session.sid in to_check_by_sid
        ):
            continue
        if stored_session.uid is None:
            resolved_by_sid[stored_session.sid] = stored_session
            continue
        stored = stored_by_sid.get(stored_session.sid)
        if stored is None:
            continue
        if "next_sid" in stored:
            stored = store.get(stored["next_sid"])
            if stored.is_new:
                continue
        store.delete_old_sessions(stored)
        if "deletion_time" in stored and stored["deletion_time"] <= now:
            continue
        to_check_by_sid[stored_session.sid] = stored
    if not to_check_by_sid:
        return resolved_by_sid
    from odoo.addons.bus.session_helpers import _get_session_token_query_params

    uids = {session.uid for session in to_check_by_sid.values()}
    query_params = _get_session_token_query_params(cr, uids)
    cr.execute(
        SQL(
            "SELECT %(select)s FROM %(from)s %(joins)s "
            "WHERE %(where)s GROUP BY %(group_by)s",
            **query_params,
        ),
    )
    id_idx = next(i for i, column in enumerate(cr.description) if column.name == "id")
    keys_by_uid = {}
    for row in cr.fetchall():
        field_values = tuple(
            (column.name, row[index]) for index, column in enumerate(cr.description)
        )
        key_tuple = tuple((k, v) for k, v in field_values if v is not None)
        keys_by_uid[row[id_idx]] = str(key_tuple).encode()
    for given_sid, stored_session in to_check_by_sid.items():
        key = keys_by_uid.get(stored_session.uid)
        if not key:
            continue
        token = hmac.new(key, stored_session.sid.encode(), hashlib.sha256).hexdigest()
        if consteq(token, stored_session.session_token):
            resolved_by_sid[given_sid] = stored_session
    return resolved_by_sid


def _patch_bus():
    from odoo.addons.bus import bus_dispatcher, session_helpers

    # bus_dispatcher imports check_sessions by name, so both are patched
    session_helpers.check_sessions = bus_dispatcher.check_sessions = check_sessions


# session_store() is cached and imported by name in many places: patch the class
# it builds and drop the cache, instead of replacing the function.
if os.environ.get("SESSION_DB_URI"):
    _logger.debug("Monkey patching session store")
    http_session.SessionStore = PGSessionStore
    # session_store() passes config.session_dir to the store, and that property
    # asserts the directory is writable. This store never uses it, so the
    # filestore can stay read-only. session_store() is its only reader.
    type(odoo.tools.config).session_dir = property(
        lambda self: os.path.join(tempfile.gettempdir(), "session_db_unused")
    )
    http_session.session_store.cache_clear()
    _patch_bus()
