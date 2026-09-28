# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime as dt
import logging
import os
import os.path
import re
import selectors
import subprocess as sp
import sys
import threading
import time
from collections.abc import Sequence
from email.utils import format_datetime
from functools import cache
from io import DEFAULT_BUFFER_SIZE, BytesIO
from typing import Literal, NamedTuple
from urllib.parse import unquote

import h11

from odoo.http import root
from odoo.tools.misc import find_in_path

__all__ = ["PaperMuncherInfo", "PaperMuncherServer", "paper_muncher"]

_logger = logging.getLogger(__name__)
_logger_pipe = _logger.getChild("pipe")
_logger_process = _logger.getChild("process")

SERVER_SOFTWARE = "Odoo"
SERVER_AGENT = "Odoo"

FALLBACK_BIN_PATH = "/opt/paper-muncher/bin/paper-muncher"
WRITE_TIMEOUT = 15
SERVE_TIMEOUT = 15 * 60
CHUNK_SIZE = 8192
MAX_INCOMPLETE_EVENT_SIZE = 8192
GET_DOCUMENT_RE = re.compile(rb"^/paper-muncher/(\.|[0-9]+)\.(?:html|xhtml|xml)$")


class PaperMuncherServer:
    __slots__ = (
        "_args",
        "_conn",
        "_deadline",
        "_documents",
        "_os_env",
        "_pdf",
        "_process",
        "_request",
        "_request_body",
        "_selector",
        "_wsgi_environ",
    )

    def __init__(self, args, os_env=None, wsgi_environ=None):
        self._args = args
        self._os_env = os_env
        self._wsgi_environ = wsgi_environ or {}
        self._process = None

    def __enter__(self):
        if self._process:
            raise RuntimeError("process started already")

        self._process = sp.Popen(
            self._args,
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=(
                sys.stderr
                if logging.NOTSET < _logger_process.level <= logging.DEBUG
                else sp.DEVNULL
            ),
            env=self._os_env,
        )

        self._conn = h11.Connection(
            h11.SERVER,
            max_incomplete_event_size=MAX_INCOMPLETE_EVENT_SIZE,
        )
        return self

    def __exit__(self, *_):
        if self._process and not self._process.poll():
            try:
                self._process.terminate()
                self._process.wait(1)
            except sp.TimeoutExpired:
                self._process.kill()
        self._process = None

    def serve(self, documents: Sequence[str], *, timeout: int = SERVE_TIMEOUT):
        """Serve Paper Muncher requests until the rendered PDF is returned."""
        if not self._process:
            raise RuntimeError(
                "this function cannot be called outside of the context manager"
            )

        if not hasattr(threading.current_thread(), "query_count"):
            threading.current_thread().query_count = 0
            threading.current_thread().query_time = 0

        _logger.debug("Starting request loop, %d documents available", len(documents))
        self._deadline = time.monotonic() + timeout
        self._documents = [
            doc.encode() if isinstance(doc, str) else doc for doc in documents
        ]
        self._selector = selectors.DefaultSelector()
        with self._selector:
            self._selector.register(
                self._process.stdout, selectors.EVENT_READ, data="stdout"
            )

            while self._process.poll() is None and self._selector.get_map():
                events = self._selector.select(timeout=_remaining_time(self._deadline))
                if events:
                    chunk = os.read(self._process.stdout.fileno(), CHUNK_SIZE)
                    if logging.NOTSET < _logger_pipe.level <= logging.DEBUG:
                        _logger_pipe.debug("read %d bytes:\n%s", len(chunk), chunk)
                    else:
                        _logger.debug("read %d bytes", len(chunk))
                    self._conn.receive_data(chunk)
                    self._process_data()

        if exit_code := self._process.poll():
            raise sp.CalledProcessError(exit_code, self._args)

        return self._pdf

    def _process_data(self):
        while True:
            event = self._conn.next_event()
            _logger.debug(
                "h11 current-state=%s event=%s", self._conn.states, type(event).__name__
            )
            if event is h11.NEED_DATA:
                break
            if isinstance(event, h11.Request):
                _logger.debug(
                    "[REQ] %s %s", event.method.decode(), event.target.decode()
                )
                self._request = event
                self._request_body = bytearray()
            elif isinstance(event, h11.Data):
                self._request_body += event.data
            elif isinstance(event, h11.EndOfMessage):
                try:
                    self._process_request()
                except Exception as exc:
                    exc.add_note("upon processing %s" % self._request)
                    raise
                if self._conn.our_state is h11.MUST_CLOSE:
                    self._selector.unregister(self._process.stdout)
                    break
                self._conn.start_next_cycle()
            elif isinstance(event, h11.ConnectionClosed):
                self._selector.unregister(self._process.stdout)
                break
            else:
                raise TypeError(f"unexpected {event=} in states={self._conn.states}")

    def _process_request(self):
        if self._request.method == b"GET" and (
            match := GET_DOCUMENT_RE.match(self._request.target)
        ):
            self._handle_get_document(match[1])
        elif (
            self._request.method == b"PUT"
            and self._request.target == b"/paper-muncher/output.pdf"
        ):
            self._handle_put(self._request_body)
            _logger.debug("Got a PDF of %s bytes", len(self._request_body))
        else:
            self._handle_fallback(self._request, self._request_body)

    def _handle_get_document(self, document_index):
        """Serve one GET document request from the worker."""
        index = int(document_index) if document_index != b"." else 0
        content = self._documents[index]

        response = h11.Response(
            status_code=200,
            headers=[
                (
                    b"Date",
                    format_datetime(dt.datetime.now(dt.timezone.utc), usegmt=True),
                ),
                (b"Content-Length", str(len(content))),
                (b"Content-Type", "text/html; charset=utf-8"),
                (b"Server", SERVER_SOFTWARE),
            ],
        )
        self._send(response)
        self._send(h11.Data(data=content))
        self._send(h11.EndOfMessage())

    def _handle_put(self, body: bytes):
        assert body.startswith(b"%PDF-"), body
        self._pdf = body
        response = h11.Response(
            status_code=200,
            headers=[
                (
                    b"Date",
                    format_datetime(dt.datetime.now(dt.timezone.utc), usegmt=True),
                ),
                (b"Server", SERVER_SOFTWARE),
                (b"Content-Length", "0"),
                (b"Connection", "close"),
            ],
        )
        self._send(response)
        self._send(h11.EndOfMessage())
        self._process.stdin.close()

    def _handle_fallback(self, request: h11.Request, body: bytes):
        assert request.target.startswith(b"/"), request.target
        request_uri = request.target.decode("ascii")
        path_quoted, _, query = request_uri.partition("?")
        environ = {
            "REQUEST_METHOD": request.method.decode("ascii"),
            "SCRIPT_NAME": "",
            "PATH_INFO": unquote(path_quoted, "latin-1"),
            "QUERY_STRING": query,
            "REQUEST_URI": request_uri,
            "RAW_URI": request_uri,
            "SERVER_PROTOCOL": "HTTP/1.0",
            "SERVER_SOFTWARE": SERVER_SOFTWARE,
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "http",
            "wsgi.input": BytesIO(body),
            "wsgi.errors": sys.stderr,
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
            "wsgi.run_once": False,
        }
        headers = {
            "HTTP_" + header.upper().replace(b"-", b"_").decode("ascii"): value.decode(
                "latin-1"
            )
            for header, value in request.headers
        }
        if content_type := headers.pop("HTTP_CONTENT_TYPE", ""):
            environ["CONTENT_TYPE"] = content_type
        if content_length := headers.pop("HTTP_CONTENT_LENGTH", ""):
            environ["CONTENT_LENGTH"] = content_length
        environ.update(headers)
        environ.update(self._wsgi_environ)

        response = None
        x_sendfile = None

        def start_response(status, res_headers, exc_info=None):
            nonlocal response, x_sendfile
            status_code = int(status.partition(" ")[0])
            res_headers = [(_normalize_header(h), v) for h, v in res_headers]

            def find_header(header):
                return next((v for h, v in res_headers if h == header), None)

            if find_header(b"Connection"):
                raise ValueError("the WSGI app cannot set the Connection header")
            if find_header(b"Upgrade"):
                raise ValueError("paper-muncher does not support websocket")
            if not find_header(b"Date"):
                res_headers.insert(
                    0,
                    (
                        b"Date",
                        format_datetime(dt.datetime.now(dt.timezone.utc), usegmt=True),
                    ),
                )
            if not find_header(b"Server"):
                res_headers.append((b"Server", SERVER_AGENT))
            x_sendfile = find_header(b"X-Sendfile")
            if x_sendfile:
                index = next(
                    (
                        i
                        for i, (h, v) in enumerate(res_headers)
                        if h == b"Content-Length"
                    )
                )
                res_headers[index] = (
                    b"Content-Length",
                    str(os.path.getsize(x_sendfile)),
                )

            response = h11.Response(status_code=status_code, headers=res_headers)
            _logger.debug(
                "[RES] %s %s", request.method.decode(), request.target.decode()
            )

        response_body = root(environ, start_response)
        deadline = time.monotonic() + WRITE_TIMEOUT
        self._send(response, deadline=deadline)

        try:
            if x_sendfile:
                response_chunks = list(response_body)
                assert not any(response_chunks), response_chunks
                with open(x_sendfile, "rb") as f:
                    while chunk := f.read(DEFAULT_BUFFER_SIZE):
                        self._send(h11.Data(data=chunk), deadline=deadline)
            else:
                for chunk in response_body:
                    self._send(h11.Data(data=chunk), deadline=deadline)
                if hasattr(response_body, "close"):
                    response_body.close()
            self._send(h11.EndOfMessage(), deadline=deadline)
        except Exception:
            self._conn.send_failed()
            raise

    def _send(self, event, *, deadline=None) -> None:
        data = self._conn.send(event)
        memview = memoryview(data)
        bytes_written = 0

        if deadline is None:
            deadline = time.monotonic() + WRITE_TIMEOUT

        with selectors.DefaultSelector() as selector:
            selector.register(self._process.stdin.fileno(), selectors.EVENT_WRITE)
            while bytes_written < len(data):
                events = selector.select(timeout=_remaining_time(deadline))
                if not events:
                    raise TimeoutError("Timeout exceeded while writing to subprocess")
                bytes_written += os.write(
                    self._process.stdin.fileno(), memview[bytes_written:]
                )
                self._process.stdin.flush()

        if logging.NOTSET < _logger_pipe.level <= logging.DEBUG:
            _logger_pipe.debug("wrote %d bytes:\n%s", bytes_written, data)
        else:
            _logger.debug("wrote %d bytes", bytes_written)


def _remaining_time(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError
    return max(1, remaining)


def _normalize_header(header: str | bytes) -> bytes:
    if isinstance(header, bytes):
        header = header.decode("ascii")
    return header.replace("-", " ").title().replace(" ", "-").encode("ascii")


class PaperMuncherInfo(NamedTuple):
    state: Literal["ok", "install"]
    bin: str
    version: str


@cache
def paper_muncher() -> PaperMuncherInfo:
    bin_path = ""
    version = ""
    try:
        try:
            bin_path = find_in_path("paper-muncher")
        except OSError as exc:
            if not os.path.isfile(FALLBACK_BIN_PATH):
                raise RuntimeError("paper-muncher binary not found in PATH") from exc
            bin_path = FALLBACK_BIN_PATH

        result = sp.run(
            [bin_path, "--version"], stdout=sp.PIPE, stderr=sp.DEVNULL, check=True
        )
        version = result.stdout.decode("utf-8", errors="replace").strip()
    except (RuntimeError, OSError, sp.SubprocessError):
        _logger.info(
            "You need paper-muncher to print a pdf version of the reports.",
            exc_info=_logger.isEnabledFor(logging.DEBUG),
        )
        return PaperMuncherInfo(state="install", bin=bin_path, version=version)

    _logger.info("Will use the paper-muncher binary at %s", bin_path)
    return PaperMuncherInfo(state="ok", bin=bin_path, version=version)
