# -*- coding: utf-8 -*-
# pylint: disable=W7935, W7936, W0403

import click
import requests
import sys

UID = 'admin'
PWD = 'admin'
REALM = 'master'
DOMAIN = 'http://localhost:8080'
CLIENT_ID = 'odoo'
CLIENT_SECRET = '099d7d07-be3b-4bc6-b69e-b50ca5d0d864'
BASE_PATH = '/auth/realms/{realm}/protocol/openid-connect'
GET_TOKEN_PATH = BASE_PATH + '/token'
VALIDATE_PATH = GET_TOKEN_PATH + '/introspect'
USERINFO_PATH = BASE_PATH + '/userinfo'
# Watch out w/ official docs, they are wrong here
# https://issues.jboss.org/browse/KEYCLOAK-8615
USERS_PATH = '/auth/admin/realms/{realm}/users'
DATA_FILE = '/tmp/keycloak.json'


def do_request(method, url, **kw):
    """Unify requests handling their result."""
    handler = getattr(requests, method)
    resp = handler(url, **kw)
    click.echo('Calling %s' % url)
    if not resp.ok:
        click.echo('Something went wrong. Quitting. ')
        click.echo('Status: %s' % resp.status_code)
        if resp.reason:
            click.echo('Reason: %s' % resp.reason)
        if resp.content:
            click.echo('Result: %s' % resp.content)
        sys.exit(0)
    return resp
