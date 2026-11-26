# Copyright 2026 Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import contextlib
import contextvars
import logging

from odoo import http

_logger = logging.getLogger(__name__)

# The request that ``odoo.http.borrow_request`` took off the request stack.
borrowed_request = contextvars.ContextVar(
    "module_block_install_borrowed_request", default=None
)


def _patch_borrow_request():
    """Remember the request borrowed by ``odoo.http.dispatch_rpc``.

    ``dispatch_rpc`` (``/xmlrpc``, ``/xmlrpc/2``, ``/jsonrpc``) runs the call
    inside ``borrow_request()``, which takes the request off the stack: during
    the call ``odoo.http.request`` is unbound, as in a script run on the
    server. Keep it at hand so these calls are still seen as HTTP requests.

    ``dispatch_rpc`` looks ``borrow_request`` up in ``odoo.http`` at each call,
    so replacing it there is enough.
    """
    original = http.borrow_request
    if getattr(original, "_module_block_install", False):
        return

    @contextlib.contextmanager
    def borrow_request():
        with original() as req:
            token = borrowed_request.set(req)
            try:
                yield req
            finally:
                borrowed_request.reset(token)

    borrow_request._module_block_install = True
    http.borrow_request = borrow_request
    _logger.info("PATCHED odoo.http.borrow_request")


def post_load():
    _patch_borrow_request()
