# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import functools

import werkzeug
from werkzeug.wrappers import Response

from odoo import http


class FutureResponse:
    """
    werkzeug.Response mock class that only serves as placeholder for
    headers to be injected in the final response.
    """

    # used by werkzeug.Response.set_cookie
    charset = "utf-8"
    max_cookie_size = 4093

    def __init__(self):
        self.headers = werkzeug.datastructures.Headers()

    @functools.wraps(werkzeug.Response.set_cookie)
    def set_cookie(
        self,
        key,
        value="",
        max_age=None,
        expires=None,
        path="/",
        domain=None,
        secure=False,
        httponly=False,
        samesite=None,
    ):
        werkzeug.Response.set_cookie(
            self,
            key,
            value=value,
            max_age=max_age,
            expires=expires,
            path=path,
            domain=domain,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )


_original_WebRequest_init = http.WebRequest.__init__


def WebRequest_init(self, httprequest):
    _original_WebRequest_init(self, httprequest)
    self.future_response = FutureResponse()


http.WebRequest.__init__ = WebRequest_init


_original_get_response = http.root.__class__.get_response


def get_response(self, httprequest, result, explicit_session):
    response = _original_get_response(self, httprequest, result, explicit_session)
    if isinstance(response, Response):
        response.headers.extend(http.request.future_response.headers)
    return response


http.root.__class__.get_response = get_response
