# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.

import mock

from odoo.tests import common


ADAPTER = ('odoo.addons.base_external_dbsource_redis.models'
           '.base_external_dbsource.redis')


class TestBaseExternalDbsource(common.TransactionCase):

    def setUp(self):
        super(TestBaseExternalDbsource, self).setUp()
        self.dbsource = self.env.ref(
            'base_external_dbsource_redis.demo_redis',
        )

    def test_connection_close_redis(self):
        """ It should return True. """
        res = self.dbsource.connection_close_redis(Trie)
        self.assertTrue(res)

    @mock.patch(ADAPTER)
    def test_connection_open_redis(self, redis):
        """ It should call SQLAlchemy open """
        self.dbsource.connection_open_redis()
        redis.StrictRedis.assert_called_once_with(
            host='redis.example.com',
            port=6379,
            db=12,
            password='password',
            ssl=False,
            ssl_ca_certs=None,
            ssl_keyfile=None,
            ssl_certfile=None,
        )
