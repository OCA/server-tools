# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os.path
import urllib.parse
import subprocess

from sentry_sdk._compat import text_type
from werkzeug import datastructures

from .generalutils import get_environ
from .processor import SanitizePasswordsProcessor


def get_request_info(request):
    """
    Returns context data extracted from :param:`request`.

    Heavily based on flask integration for Sentry: https://git.io/vP4i9.
    """
    urlparts = urllib.parse.urlsplit(request.url)
    return {
        "url": "{}://{}{}".format(urlparts.scheme, urlparts.netloc, urlparts.path),
        "query_string": urlparts.query,
        "method": request.method,
        "headers": dict(datastructures.EnvironHeaders(request.environ)),
        "env": dict(get_environ(request.environ)),
    }


def get_extra_context(request):
    """
    Extracts additional context from the current request (if such is set).
    """
    try:
        session = getattr(request, "session", {})
    except RuntimeError:
        ctx = {}
    else:
        ctx = {
            "tags": {
                "database": session.get("db", None),
            },
            "user": {
                "email": session.get("login", None),
                "id": session.get("uid", None),
            },
            "extra": {
                "context": session.get("context", {}),
            },
        }
        if request.httprequest:
            ctx.update({"request": get_request_info(request.httprequest)})
    return ctx


class SanitizeOdooCookiesProcessor(SanitizePasswordsProcessor):
    """Custom :class:`raven.processors.Processor`.
    Allows to sanitize sensitive Odoo cookies, namely the "session_id" cookie.
    """

    KEYS = frozenset(
        [
            "session_id",
        ]
    )


class InvalidGitRepository(Exception):
    pass


def fetch_git_tag(path):
    """Return tag for supplied git path"""
    if not os.path.exists(path):
        raise InvalidGitRepository("Invalid git path: '%s' provided" % (path))
    os.chdir(path)
    git_tag = subprocess.check_output(["git", "describe", "--tags"])
    git_tag = git_tag.decode("utf-8").strip()
    return git_tag
