# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from urlparse import parse_qs, urlparse

from odoo import api, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.base_external_dbsource.models import (
        base_external_dbsource,
    )
    CONNECTORS = base_external_dbsource.BaseExternalDbsource.CONNECTORS
    try:
        import redis
        CONNECTORS.append(('redis', 'Redis'))
        assert redis
    except (ImportError, AssertionError):
        _logger.info('Redis not available. Please install "redis" '
                     'python package.')
except ImportError:
    _logger.info('base_external_dbsource Odoo module not found.')


class BaseExternalDbsource(models.Model):
    """Provide logic for a Redis Datasource."""

    _inherit = "base.external.dbsource"

    @api.multi
    @api.constrains('connection_string', 'connector')
    def _check_connection_string_connector_redis(self):
        """Make sure that the connection string is valid."""
        self.filtered(lambda r: r._parse_connection_string())

    @api.multi
    def connection_close_redis(self, connection):
        self.current_table = False
        return True

    @api.multi
    def connection_open_redis(self):
        server_info = self._parse_connection_string()
        password = self.password or None
        ssl = bool(self.ca_certs)
        self.current_table = True
        return redis.StrictRedis(
            host=server_info['host'],
            port=server_info['port'],
            db=server_info['db'],
            password=password,
            ssl=ssl,
            ssl_ca_certs=self.ca_certs or None,
            ssl_keyfile=self.client_key or None,
            ssl_certfile=self.client_cert or None,
        )

    @api.multi
    def execute_redis(self, *args, **kwargs):
        raise NotImplementedError(_(
            'A generic Redis executor is not available. Use the CRUD '
            'methods.',
        ))

    @api.multi
    def remote_browse_redis(self, keys):
        """Return the key values.

        Args:
            keys (iter): Keys to get

        Returns:
            dict: Results, keyed by key
        """
        with self.connection_open() as redis:
            return {k: redis.get(k) for k in keys}

    @api.multi
    def remote_create_redis(self, vals, ex=None, px=None):
        """Create the key/values on Redis.

        Args:
            vals (dict): Key/Value pairs to set.
            ex (int, optional): Sets an expire flag for this amount of
            seconds.
            px (int, optional): Sets an expire flag for this amount of
            milliseconds.

        Returns:
            dict of bool: Success by key.
        """
        return self.remote_set_redis(vals, ex, px, nx=True)

    @api.multi
    def remote_delete_redis(self, keys):
        """Delete the keys from Redis.

        Args:
            keys (iter): Keys to delete.
        """
        with self.connection_open() as redis:
            return redis.delete(keys)

    @api.multi
    def remote_update_redis(self, vals, ex=None, px=None):
        """Update the key/values on Redis.

        Args:
            vals (dict): Key/Value pairs to set.
            ex (int, optional): Sets an expire flag for this amount of
            seconds.
            px (int, optional): Sets an expire flag for this amount of
            milliseconds.

        Returns:
            dict of bool: Success by key.
        """
        return self.remote_set_redis(vals, ex, px, xx=True)

    @api.multi
    def remote_set_redis(self, vals, ex=None, px=None, nx=False, xx=False):
        """Create or set the key/values on Redis.

        Args:
            vals (dict): Key/Value pairs to set.
            ex (int, optional): Sets an expire flag for this amount of
            seconds.
            px (int, optional): Sets an expire flag for this amount of
            milliseconds.
            nx (bool, optional): Only set value if key does not exist.
            xx (bool, optional): Only set value if the key already exists.

        Returns:
            dict of bool: Success by key.
        """
        with self.connection_open() as redis:
            return {
                k: redis.set(k, v, ex, px, nx, xx) for k, v in vals.items()
            }

    @api.multi
    def _parse_connection_string(self):
        """Parse the connection string and return a dict."""
        self.ensure_one()
        parsed = urlparse(self.connection_string)
        query = parse_qs(parsed.query)
        if parsed.scheme and parsed.scheme != 'redis':
            raise ValidationError(_(
                'Connection string must be prefixed with redis://',
            ))
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 6379,
            'db': query.get('db', 0),
        }
