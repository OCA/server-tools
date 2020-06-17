# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.tools.cache import STAT


class TestIrConfigParameter(common.TransactionCase):

    def setUp(self):
        super(TestIrConfigParameter, self).setUp()
        self.param_obj = self.env['ir.config_parameter']
        self.data_obj = self.env['ir.model.data']
        self.delay = self.env.ref(
            'auth_session_timeout.inactive_session_time_out_delay')

    def test_check_session_param_delay(self):
        delay = self.param_obj._auth_timeout_get_parameter_delay()
        self.assertEqual(delay, int(self.delay.value))
        self.assertIsInstance(delay, int)

    def test_check_session_param_urls(self):
        urls = self.param_obj._auth_timeout_get_parameter_ignored_urls()
        self.assertIsInstance(urls, list)


class TestIrConfigParameterCaching(common.TransactionCase):

    def setUp(self):
        super(TestIrConfigParameterCaching, self).setUp()
        self.param_obj = self.env['ir.config_parameter']

    def _cache(self, func_name):
        return STAT[(
            self.env.cr.dbname, 'ir.config_parameter',
            getattr(self.env['ir.config_parameter'], func_name).__wrapped__,
        )]

    def test_auth_timeout_get_parameter_delay_cache(self):
        """First call should actually run the function."""
        cache = self._cache('_auth_timeout_get_parameter_delay')
        cache_misses = cache.miss
        self.param_obj._auth_timeout_get_parameter_delay()
        self.assertEqual(cache.miss, cache_misses + 1)

    def test_auth_timeout_get_parameter_ignored_urls_cache(self):
        """First call should actually run the function."""
        cache = self._cache('_auth_timeout_get_parameter_ignored_urls')
        cache_misses = cache.miss
        self.param_obj._auth_timeout_get_parameter_ignored_urls()
        self.assertEqual(cache.miss, cache_misses + 1)

    def test_check_param_writes_clear_delay_cache(self):
        self.param_obj._auth_timeout_get_parameter_delay()
        cache = self._cache('_auth_timeout_get_parameter_delay')
        cache_misses = cache.miss
        self.param_obj.set_param('inactive_session_time_out_delay', 7201)
        self.param_obj._auth_timeout_get_parameter_delay()
        self.assertEqual(cache.miss, cache_misses + 1)

    def test_check_param_writes_clear_ignore_url_cache(self):
        self.param_obj._auth_timeout_get_parameter_ignored_urls()
        cache = self._cache('_auth_timeout_get_parameter_ignored_urls')
        cache_misses = cache.miss
        self.param_obj.set_param('inactive_session_time_out_ignored_url',
                                 'example.com')
        self.param_obj._auth_timeout_get_parameter_ignored_urls()
        self.assertEqual(cache.miss, cache_misses + 1)
