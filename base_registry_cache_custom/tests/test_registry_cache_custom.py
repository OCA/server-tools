# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo_test_helper import FakeModelLoader

from odoo import models
from odoo.modules import registry
from odoo.tests.common import TransactionCase
from odoo.tools.cache import get_cache_key_counter, ormcache
from odoo.tools.misc import mute_logger

from odoo.addons.base_registry_cache_custom.exceptions import (
    CacheInvalidConfigError,
    CacheInvalidDependencyError,
    CacheInvalidNameError,
)
from odoo.addons.base_registry_cache_custom.registry import add_custom_cache


class TestRegistryCacheCustom(TransactionCase):
    def setUp(self):
        super().setUp()
        # Prepare a backup of the ``registry`` module attributes to be able to restore
        # them once each test is over to avoid polluting other tests
        self.__REGISTRY_CACHES_BACKUP = dict(registry._REGISTRY_CACHES)
        self.__CACHES_BY_KEY_BACKUP = dict(registry._CACHES_BY_KEY)

    def tearDown(self):
        # Restore ``registry`` module attributes
        registry._REGISTRY_CACHES = dict(self.__REGISTRY_CACHES_BACKUP)
        registry._CACHES_BY_KEY = dict(self.__CACHES_BY_KEY_BACKUP)
        super().tearDown()

    @mute_logger("odoo.addons.base_registry_cache_custom.registry")
    def test_01_add_custom_cache(self):
        """Base checks for adding custom caches

        Checks that ``add_custom_cache()`` adds the new cache to all DBs' registries,
        and that the signaling setup is correctly done for each DB
        """
        add_custom_cache("test_cache", 10)
        for db_registry in type(self.env.registry).registries.d.values():
            self.assertIn("test_cache", db_registry._Registry__caches)
            self.assertEqual(db_registry._Registry__caches["test_cache"].count, 10)
            with db_registry.cursor() as cr:
                cr.execute(
                    """
                    SELECT sequence_name
                    FROM information_schema.sequences
                    WHERE sequence_name = 'base_cache_signaling_test_cache'
                    """
                )
                self.assertEqual(cr.fetchall(), [("base_cache_signaling_test_cache",)])
                self.assertIn("test_cache", db_registry.get_sequences(cr)[1])

    @mute_logger("odoo.addons.base_registry_cache_custom.registry")
    def test_02_add_custom_cache_count(self):
        """Checks that using ``count <= 0`` creates caches w/ ``count = 1``"""
        for name, count in (("test_cache_zero", 0), ("test_cache_negative", -1)):
            add_custom_cache(name, count)
            for db_registry in type(self.env.registry).registries.d.values():
                self.assertEqual(db_registry._Registry__caches[name].count, 1)

    @mute_logger("odoo.addons.base_registry_cache_custom.registry")
    def test_03_add_custom_cache_existing(self):
        """Checks a warning is logged when trying to add an existing cache"""
        add_custom_cache("test_cache", 10)
        logname = "odoo.addons.base_registry_cache_custom.registry"
        with self.assertLogs(logname, "WARNING") as log:
            add_custom_cache("test_cache", 50)
        self.assertEqual(len(log.output), 1)
        self.assertEqual(
            log.output[0],
            "WARNING:odoo.addons.base_registry_cache_custom.registry:"
            "Cache 'test_cache' already exists, skipping...",
        )
        self.assertEqual(registry._REGISTRY_CACHES["test_cache"], 10)

    @mute_logger("odoo.addons.base_registry_cache_custom.registry")
    def test_04_add_custom_cache_dotted_name_invalid(self):
        """Checks a ``CacheInvalidNameError`` is raised when trying to use a dotted name

        This exception is raised when trying to use a dotted name for a cache that
        allows direct invalidation
        """
        with self.assertRaisesRegex(
            CacheInvalidNameError, r"^Invalid cache name 'test\.cache'$"
        ):
            add_custom_cache("test.cache", 10)

    @mute_logger("odoo.addons.base_registry_cache_custom.registry")
    def test_05_add_custom_cache_dependent(self):
        """Checks creation of caches whose invalidation depend on another cache"""
        add_custom_cache("test_cache_1", 10)
        add_custom_cache("test_cache_2", 10, depends_on_caches=["test_cache_1"])
        add_custom_cache("test_cache_3", 10, depends_on_caches=["test_cache_1"])
        add_custom_cache(
            "test_cache_4", 10, depends_on_caches=["test_cache_2", "test_cache_3"]
        )
        db_registry = self.env.registry

        def _fill_caches():
            for i in range(1, 5):
                db_registry._Registry__caches[f"test_cache_{i}"]["key"] = 1

        # Put some data in the caches, then invalidate the parent cache and check that
        # the cache itself and all dependent caches are empty
        _fill_caches()
        db_registry.clear_cache("test_cache_1")
        self.assertFalse(db_registry._Registry__caches["test_cache_1"])
        self.assertFalse(db_registry._Registry__caches["test_cache_2"])
        self.assertFalse(db_registry._Registry__caches["test_cache_3"])
        self.assertFalse(db_registry._Registry__caches["test_cache_4"])

        _fill_caches()
        db_registry.clear_cache("test_cache_2")
        self.assertEqual(db_registry._Registry__caches["test_cache_1"]["key"], 1)
        self.assertFalse(db_registry._Registry__caches["test_cache_2"])
        self.assertEqual(db_registry._Registry__caches["test_cache_3"]["key"], 1)
        self.assertFalse(db_registry._Registry__caches["test_cache_4"])

        _fill_caches()
        db_registry.clear_cache("test_cache_3")
        self.assertEqual(db_registry._Registry__caches["test_cache_1"]["key"], 1)
        self.assertEqual(db_registry._Registry__caches["test_cache_2"]["key"], 1)
        self.assertFalse(db_registry._Registry__caches["test_cache_3"])
        self.assertFalse(db_registry._Registry__caches["test_cache_4"])

        _fill_caches()
        db_registry.clear_cache("test_cache_4")
        self.assertEqual(db_registry._Registry__caches["test_cache_1"]["key"], 1)
        self.assertEqual(db_registry._Registry__caches["test_cache_2"]["key"], 1)
        self.assertEqual(db_registry._Registry__caches["test_cache_3"]["key"], 1)
        self.assertFalse(db_registry._Registry__caches["test_cache_4"])

    @mute_logger("odoo.addons.base_registry_cache_custom.registry")
    def test_06_add_custom_cache_no_direct_invalidation(self):
        """Checks creation of caches that cannot be directly invalidated"""
        add_custom_cache("test_cache_1", 10)
        add_custom_cache(
            # Cannot be directly invalidated => no DB sequence => can use dotted name
            "test.cache.2",
            10,
            depends_on_caches=["test_cache_1"],
            allows_direct_invalidation=False,
        )
        add_custom_cache(
            "test_cache_3",
            10,
            depends_on_caches=["test_cache_1"],
            allows_direct_invalidation=False,
        )

        # ``Registry.clear_cache()`` first checks whether the cache name is not dotted
        with self.assertRaises(AssertionError):
            self.env.registry.clear_cache("test.cache.2")

        # ``Registry.clear_cache()`` then access ``_CACHE_BY_KEY`` to get dependent
        # caches to invalidate, but "test_cache_3" does not allow direct invalidation,
        # so it's not included in that mapping
        with self.assertRaises(KeyError):
            self.env.registry.clear_cache("test_cache_3")

        # A cache that doesn't allow direct invalidation requires a parent cache
        with self.assertRaisesRegex(
            CacheInvalidConfigError,
            r"^Cache 'test_cache_4' should either allow direct invalidation"
            " or depend on another cache for indirect invalidation$",
        ):
            add_custom_cache("test_cache_4", 10, allows_direct_invalidation=False)

        # Parent caches must exist
        with self.assertRaisesRegex(
            CacheInvalidDependencyError,
            r"^Cache 'test_cache_5' cannot depend on cache 'test_cache_6':"
            " 'test_cache_6' doesn't exist or doesn't allow direct invalidation$",
        ):
            add_custom_cache(
                "test_cache_5",
                10,
                depends_on_caches=["test_cache_6"],
                allows_direct_invalidation=False,
            )

        # Parent caches must allow direct invalidation
        with self.assertRaisesRegex(
            CacheInvalidDependencyError,
            r"^Cache 'test_cache_6' cannot depend on cache 'test_cache_3':"
            " 'test_cache_3' doesn't exist or doesn't allow direct invalidation$",
        ):
            add_custom_cache(
                "test_cache_6",
                10,
                depends_on_caches=["test_cache_3"],
                allows_direct_invalidation=False,
            )

    @mute_logger("odoo.addons.base_registry_cache_custom.registry")
    def test_07_add_custom_cache_ormcache_usage_and_invalidation(self):
        """Checks usage of custom caches for the ``@ormcache`` decorator"""
        add_custom_cache("test_cache_1", 10)
        add_custom_cache(
            "test_cache_2",
            10,
            depends_on_caches=["test_cache_1"],
            allows_direct_invalidation=True,
        )

        cls = type(self)
        loader = FakeModelLoader(cls.env, cls.__module__)
        loader.backup_registry()

        class Base(models.BaseModel):
            _inherit = "base"

            @ormcache("param", cache="test_cache_1")
            def func_1(self, param: str):
                return tuple(self.ids), param

            @ormcache("param", cache="test_cache_2")
            def func_2(self, param: str):
                return tuple(self.ids), param

        loader.update_registry([Base])
        func_1 = self.env["base"].func_1
        func_2 = self.env["base"].func_2

        # Prepare params to check
        # NB: ``counter.hit|miss`` will count how many times the value has been
        # retrieved from the cache (hit) or by executing the cached function (miss)
        cache_1, key_1, counter_1 = get_cache_key_counter(func_1, "param-1")
        hit_1 = counter_1.hit
        miss_1 = counter_1.miss
        cache_2, key_2, counter_2 = get_cache_key_counter(func_2, "param-2")
        hit_2 = counter_2.hit
        miss_2 = counter_2.miss

        # Clear parent cache to clear both caches
        self.env.registry.clear_cache("test_cache_1")
        self.assertNotIn(key_1, cache_1)
        self.assertNotIn(key_2, cache_2)

        # Execute the functions, check counters
        func_1("param-1")
        self.assertEqual(counter_1.hit, hit_1)
        self.assertEqual(counter_1.miss, miss_1 + 1)
        self.assertIn(key_1, cache_1)
        func_2("param-2")
        self.assertEqual(counter_2.hit, hit_2)
        self.assertEqual(counter_2.miss, miss_2 + 1)
        self.assertIn(key_2, cache_2)
        func_1("param-1")
        self.assertEqual(counter_1.hit, hit_1 + 1)
        self.assertEqual(counter_1.miss, miss_1 + 1)
        self.assertIn(key_1, cache_1)
        func_2("param-2")
        self.assertEqual(counter_2.hit, hit_2 + 1)
        self.assertEqual(counter_2.miss, miss_2 + 1)
        self.assertIn(key_2, cache_2)

        # Clear parent cache to clear both caches (again)
        self.env.registry.clear_cache("test_cache_1")
        self.assertNotIn(key_1, cache_1)
        self.assertNotIn(key_2, cache_2)

        # Execute the functions, check counters (again)
        func_1("param-1")
        self.assertEqual(counter_1.hit, hit_1 + 1)
        self.assertEqual(counter_1.miss, miss_1 + 2)
        self.assertIn(key_1, cache_1)
        func_2("param-2")
        self.assertEqual(counter_2.hit, hit_2 + 1)
        self.assertEqual(counter_2.miss, miss_2 + 2)
        self.assertIn(key_2, cache_2)
        func_1("param-1")
        self.assertEqual(counter_1.hit, hit_1 + 2)
        self.assertEqual(counter_1.miss, miss_1 + 2)
        self.assertIn(key_1, cache_1)
        func_2("param-2")
        self.assertEqual(counter_2.hit, hit_2 + 2)
        self.assertEqual(counter_2.miss, miss_2 + 2)
        self.assertIn(key_2, cache_2)

        # Clear dependent cache only this time
        self.env.registry.clear_cache("test_cache_2")
        self.assertIn(key_1, cache_1)
        self.assertNotIn(key_2, cache_2)

        # Execute the functions, check counters (again): this time the ``hit`` value
        # for the parent cache will increase when we run ``func_1`` again, while the
        # ``miss`` value of the dependent cache should increase when calling ``func_2``
        func_1("param-1")
        self.assertEqual(counter_1.hit, hit_1 + 3)
        self.assertEqual(counter_1.miss, miss_1 + 2)
        self.assertIn(key_1, cache_1)
        func_2("param-2")
        self.assertEqual(counter_2.hit, hit_2 + 2)
        self.assertEqual(counter_2.miss, miss_2 + 3)
        self.assertIn(key_2, cache_2)

        # Reset models registry
        loader.restore_registry()
