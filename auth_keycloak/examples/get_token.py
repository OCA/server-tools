# -*- coding: utf-8 -*-
# pylint: disable=W7935, W7936, W0403

import click
from urlparse import urljoin
import json

from common import (
    UID, PWD,
    CLIENT_ID, CLIENT_SECRET,
    DATA_FILE, DOMAIN, REALM,
    GET_TOKEN_PATH,
    do_request
)


@click.command()
@click.option('--domain', default=DOMAIN)
@click.option('--realm', default=REALM)
@click.option(
    '--username',
    prompt='Username',
    help='Username to authenticate.',
    default=UID)
@click.option(
    '--password',
    prompt='Password',
    default=PWD)
@click.option(
    '--client_id',
    prompt='Client ID',
    help='Keycloak client ID.',
    default=CLIENT_ID)
@click.option(
    '--client_secret',
    prompt='Client secret',
    help='Keycloak client secret.',
    default=CLIENT_SECRET)
def get_token(**kw):
    """Retrieve auth token."""
    data = kw.copy()
    data['grant_type'] = 'password'
    token = _get_token(data)
    data['token'] = token
    with open(DATA_FILE, 'w') as ff:
        ff.write(json.dumps(data))
        click.echo('Saved to %s' % DATA_FILE)
    return token


def _get_token(data):
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    url = urljoin(data['domain'], GET_TOKEN_PATH.format(realm=data['realm']))
    resp = do_request('post', url, data=data, headers=headers)
    click.echo('Access token:')
    click.echo(resp.json()['access_token'])
    return resp.json()['access_token']


if __name__ == '__main__':
    get_token()
