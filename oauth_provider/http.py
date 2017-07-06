# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json

from werkzeug.exceptions import BadRequest

from odoo import http


old_handle_exception = http.JsonRequest._handle_exception
old_json_response = http.JsonRequest._json_response
old_init = http.JsonRequest.__init__


def __init__(self, *args):
    try:
        old_init(self, *args)
    except BadRequest as e:
        try:
            args = self.httprequest.args
            self.jsonrequest = args
            self.params = json.loads(self.jsonrequest.get('params', "{}"))
            self.context = self.params.pop('context',
                                           dict(self.session.context))
        except ValueError:
            raise e


def _handle_exception(self, exception):
    """ Override the original method to handle Werkzeug exceptions.

    Args:
        exception (Exception): Exception object that is being thrown.

    Returns:
        BaseResponse: JSON Response.
    """

    # For some reason a try/except here still raised...
    code = getattr(exception, 'code', None)
    if code is None:
        return old_handle_exception(
            self, exception,
        )

    error = {
        'data': http.serialize_exception(exception),
        'code': code,
    }

    try:
        error['message'] = exception.description
    except AttributeError:
        try:
            error['message'] = exception.message
        except AttributeError:
            error['message'] = 'Internal Server Error'

    return self._json_response(error=error)


def _json_response(result=None, error=None, headers=None, status=None):
    """ Returns a JSON response to the OAuth client.

    This is mainly provided as a compatibility layer for old methods.

    The true solution to all of this is to design a new Request type and
    somehow use that instead of JSON-RPC. That's a lot of work though, so
    this instead.

    Args:
        result (mixed, optional): User's requested data.
        error (dict, optional): Serialized error data (from
            `_handle_exception`).
        jsonrpc (bool, optional): Set to False in order to respond without
            JSON-RPC, and instead send a simple JSON response.
        headers (dict, optional): Mapping of headers to apply to the
            request. If the `Content-Type` header is not defined,
             `application/json` will automatically be added.

    Returns:
        Response: Werkzeug response object based on the input.
    """

    if headers is None:
        headers = {}

    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'

    body = json.dumps(result or error)
    headers['Content-Length'] = len(body)

    return http.Response(
        body,
        status=status or (error and error.get('code', 200)) or 200,
        headers=headers,
    )
