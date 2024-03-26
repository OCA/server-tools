# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from itertools import product
from pathlib import Path
from random import choice

from lxml import etree

from odoo.tests.common import SavepointCase
from odoo.tools import get_cache_key_counter


class TestFullArch(SavepointCase):
    """Tests full arch computations

    Test views are defined in ``demo/ir_ui_view.xml``

    The views' inheritance follows this schema:

          V1
         /  \
       V2    V3 <- primary
      / |     |
    V4  V5    V6

    According to Odoo's current inheriting system and its workflow for combining views,
    we expect the V1 full architecture to include modifications made by V2, V4 and V5,
    while V3's full architecture should include V1's full architecture and V6's arch
    """

    @property
    def data_path(self):
        return Path(__file__).parent.absolute() / "data"

    @classmethod
    def _get_views_by_xmlids_num(cls, nums):
        env = cls.env
        base_xmlid = "base_view_full_arch.demo_view_%s"
        return sum([env.ref(base_xmlid % n) for n in nums], env["ir.ui.view"])

    def _compare_with_file(self, view, fpath):
        with open(fpath) as expected:
            self.assertEqual(view.full_arch.strip(), expected.read().strip())

    def test_00_format_doc(self):
        """Tests formatting methods without inheritance"""
        self._compare_with_file(
            self.env.ref("base_view_full_arch.test_format_doc"),
            Path(__file__).parent / "data" / "test_00_format_doc.xml",
        )

    def test_01_root_view_full_arch(self):
        """Tests full architecture for root view (inherit_id = False)"""
        view_1 = self._get_views_by_xmlids_num([1])
        self.assertFalse(view_1.inherit_id)
        self.assertEqual(view_1._get_ancestor(), view_1)
        self.assertEqual(view_1._get_root(), view_1)
        fpath = self.data_path / "test_01_root_view_full_arch.xml"
        self._compare_with_file(view_1, fpath)

    def test_02_ancestor_view_full_arch(self):
        """Tests full architecture for ancestor view (mode = "primary")"""
        view_1, view_3 = self._get_views_by_xmlids_num([1, 3])
        self.assertEqual(view_3.mode, "primary")
        self.assertEqual(view_3._get_ancestor(), view_3)
        self.assertEqual(view_3._get_root(), view_1)
        fpath = self.data_path / "test_02_ancestor_view_full_arch.xml"
        self._compare_with_file(view_3, fpath)

    def test_03_inheriting_view_full_arch(self):
        """Tests root, ancestors and full architectures for inheriting views"""
        views = v1, v2, v3, v4, v5, v6 = self._get_views_by_xmlids_num(range(1, 7))

        # v1 is common root for every view
        self.assertTrue(all(v._get_root() == v1 for v in (v1, v2, v3, v4, v5, v6)))

        # v1 is ancestor for v1 itself, v2, v4 and v5
        self.assertTrue(all(v._get_ancestor() == v1 for v in (v1, v2, v4, v5)))

        # v3 is ancestor for v3 itself and v6
        self.assertTrue(all(v._get_ancestor() == v3 for v in (v3, v6)))

        # Each view shares the same full architecture of its ancestor
        for view in views:
            self.assertEqual(view.full_arch, view._get_ancestor().full_arch)

    def test_04_archive_inheriting_view(self):
        """Tests that archiving views affects other views' ``full_arch``"""
        view_1, view_4, view_5 = self._get_views_by_xmlids_num([1, 4, 5])
        (view_4 + view_5).action_archive()
        fpath = self.data_path / "test_04_archive_inheriting_view.xml"
        self._compare_with_file(view_1, fpath)

    def test_05_update_views_arch_propagate_top_down(self):
        """Tests that changes upon views' arch are propagated top-down

        In this test, we're changing the architecture for view 1 and checking whether
        the change is propagated down to all views, to make sure that changes are
        propagated top-down even if there's a primary view (view 3) between the
        view that is updated (view 1) and the one upon which the change should be
        propagated (view 6)
        """
        v1, v2, v3, v4, v5, v6 = self._get_views_by_xmlids_num(range(1, 7))

        # Make field ``name`` required in view 1
        doc_1 = etree.fromstring(v1.arch)
        attr = doc_1.find(".//field[@name='name']")
        attr.set("required", "1")
        v1.arch = etree.tostring(doc_1)

        fname = "test_05_update_views_arch_propagate_top_down_ancestor_is_v%s.xml"
        for ancestor_id, views in {1: [v1, v2, v4, v5], 3: [v3, v6]}.items():
            fpath = self.data_path / (fname % str(ancestor_id))
            for view in views:
                self._compare_with_file(view, fpath)

    def test_06_update_views_arch_propagate_bottom_up(self):
        """Tests that changes upon views' arch are propagated bottom-up

        In this test, we're changing the architecture for view 6 and checking whether
        the change is propagated up to the other views; however, this time view 3 will
        function as a blocker, since it's a primary view: changes made to view 3 or any
        of its inheriting views will not be propagated to view 1 or any of the views
        that have view 1 as ancestor
        """
        v1, v2, v3, v4, v5, v6 = self._get_views_by_xmlids_num(range(1, 7))

        # View 6 will make field ``groups_id`` readonly; we'll change the target of
        # the attribute so that field ``name`` will be readonly
        doc_6 = etree.fromstring(v6.arch)
        doc_6.set("name", "name")  # ``doc_6``'s root tag is ``groups_id`` field itself
        v6.arch = etree.tostring(doc_6)

        fname = "test_06_update_views_arch_propagate_bottom_up_ancestor_is_v%s.xml"
        for ancestor_id, views in {1: [v1, v2, v4, v5], 3: [v3, v6]}.items():
            fpath = self.data_path / (fname % str(ancestor_id))
            for view in views:
                self._compare_with_file(view, fpath)

    def test_07_check_traverse_inherit_id_caching(self):
        """Tests ``_traverse_inherit_id()`` cache"""

        def _test_cache():
            couples = tuple(product(views, [True, False]))
            # Check no value is cached
            for view, value in couples:
                cache, key, _ = get_cache_key_counter(view._traverse_inherit_id, value)
                self.assertNotIn(key, cache)
            # Cache results
            for view, value in couples:
                view._traverse_inherit_id(value)
            # Check values have been cached
            for view, value in couples:
                cache, key, _ = get_cache_key_counter(view._traverse_inherit_id, value)
                self.assertIn(key, cache)

        views = self._get_views_by_xmlids_num(range(1, 7))

        # Clear method cache before starting
        view_obj = self.env["ir.ui.view"]
        type(view_obj)._traverse_inherit_id.clear_cache(view_obj)
        _test_cache()

        # Change a random view's mode
        choice(views).mode = "primary"
        _test_cache()

        # Force demo_view_3 to inherit from demo_view_5 instead of demo_view_1
        views[2].inherit_id = views[4]
        _test_cache()

        # Delete one of the children views which is not inherited by any other view
        choice(views.filtered(lambda v: not v.inherit_children_ids)).unlink()
        views = views.exists()  # Remove deleted view
        _test_cache()
