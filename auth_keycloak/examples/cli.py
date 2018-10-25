# -*- coding: utf-8 -*-
# pylint: disable=W7935, W7936, W0403

import click
from urlparse import urljoin
import os
import sys
import json
from get_token import get_token
from common import (
    DATA_FILE, VALIDATE_PATH,
    USERINFO_PATH, USERS_PATH,
    do_request
)


def _read_data():
    if not os.path.isfile(DATA_FILE):
        click.echo('You must run `get_token` before.')
        sys.exit(0)
    with open(DATA_FILE, 'r') as ff:
        return json.loads(ff.read())


@click.group()
@click.pass_context
def cli(ctx, **kw):
    ctx.params.update(_read_data())


@cli.command()
@click.pass_context
def user_info(ctx, **kw):
    """Retrieve user info."""
    params = ctx.parent.params
    url = urljoin(
        params['domain'], USERINFO_PATH.format(realm=params['realm'])
    )
    headers = {
        'Authorization': 'Bearer %s' % params['token'],
    }
    resp = do_request('get', url, headers=headers)
    click.echo('User info:')
    click.echo(resp.json())
    return resp.json()


@cli.command()
@click.option(
    '--search',
    help='Search string, see API.',
)
@click.pass_context
def search_users(ctx, search=None, **kw):
    """Retrieve users info."""
    params = ctx.parent.params
    url = urljoin(
        params['domain'],
        USERS_PATH.format(realm=params['realm'])
    )
    if search:
        url += '?search={}'.format(search)
    headers = {
        'Authorization': 'Bearer %s' % params['token'],
    }
    resp = do_request('get', url, headers=headers)
    click.echo('User info:')
    click.echo(resp.json())
    return resp.json()


@cli.command()
@click.option(
    '--username',
    required=True
)
@click.option(
    '--values',
    help='Values mapping like "key:value;key1:value1", see API.',
)
@click.pass_context
def create_user(ctx, username, values=None, **kw):
    """Create user."""
    params = ctx.parent.params
    url = urljoin(
        params['domain'],
        USERS_PATH.format(realm=params['realm'])
    )
    data = {
        'username': username,
        'enabled': True,
        'email': username + '@test.com',
        'emailVerified': True,
    }
    if values:
        for pair in values.split(';'):
            data[pair.split(':')[0]] = pair.split(':')[1]

    headers = {
        'Authorization': 'Bearer %s' % params['token'],
    }
    resp = do_request('post', url, headers=headers, json=data)
    # crate user does not give back any value :(
    click.echo('User created.')
    return resp.ok


@cli.command()
@click.pass_context
def validate_token(ctx, **kw):
    """Validate authentication token."""
    params = ctx.parent.params
    if not params:
        # invoked via context
        params = _read_data()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = {
        'token': params['token']
    }
    url = urljoin(
        params['domain'], VALIDATE_PATH.format(realm=params['realm'])
    )
    click.echo('Calling %s' % url)
    resp = do_request(
        'post',
        url,
        data=data,
        auth=(params['client_id'], params['client_secret']),
        headers=headers,
    )
    result = resp.json()
    if not result.get('active'):
        # token expired
        click.echo('Token expired, running get token again...')
        ctx.invoke(get_token)
        ctx.forward(validate_token)
    click.echo(result)
    return resp.json()


if __name__ == '__main__':
    cli()
