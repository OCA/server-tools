from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from .. import compare


def record(model, module, model_type=""):
    """Build a model record shaped like the ones ``compare_model_sets`` gets."""
    return {"model": model, "module": module, "model_type": model_type}


def apriori(
    renamed_modules=None,
    merged_modules=None,
    renamed_models=None,
    merged_models=None,
):
    """Build a stand-in for the ``openupgrade_scripts.apriori`` knowledge base."""
    return SimpleNamespace(
        renamed_modules=renamed_modules or {},
        merged_modules=merged_modules or {},
        renamed_models=renamed_models or {},
        merged_models=merged_models or {},
    )


class TestCompareModelSets(TestCase):
    """Test the model-level reports produced by ``compare_model_sets``.

    ``compare.py`` is plain Python: it only needs ``apriori`` from
    ``openupgrade_scripts``, and falls back to empty mappings when that import is
    unavailable. So these tests need no Odoo instance, no registry and no
    database, and they run under the Odoo test runner as well as standalone.
    """

    def run_compare(self, old_records, new_records, **apriori_kwarg):
        with patch.object(compare, "apriori", apriori(**apriori_kwarg)):
            return dict(compare.compare_model_sets(old_records, new_records))

    def test_unchanged_model_is_not_reported(self):
        """A model present in both sets, in the same module, produces nothing."""
        records = [record("sale.order", "sale")]
        self.assertEqual(self.run_compare(records, list(records)), {})

    def test_new_model(self):
        """A model only in the new set is reported under its module and general."""
        old_records = [record("sale.order", "sale")]
        new_records = old_records + [record("sale.advance", "sale")]
        self.assertEqual(
            self.run_compare(old_records, new_records),
            {
                "sale": ["new model sale.advance"],
                "general": ["new model sale.advance [module sale]"],
            },
        )

    def test_obsolete_model(self):
        """A model only in the old set is reported under its module and general."""
        old_records = [record("sale.order", "sale"), record("sale.legacy", "sale")]
        new_records = [record("sale.order", "sale")]
        self.assertEqual(
            self.run_compare(old_records, new_records),
            {
                "sale": ["obsolete model sale.legacy"],
                "general": ["obsolete model sale.legacy [module sale]"],
            },
        )

    def test_model_moved_to_another_module(self):
        """A module move is reported from the old side, then from the new one.

        Only the old module gets the "moved to" line and only the new module the
        "moved from" line; neither is repeated under ``general``.
        """
        old_records = [record("sale.order", "sale")]
        new_records = [record("sale.order", "account")]
        self.assertEqual(
            self.run_compare(old_records, new_records),
            {
                "sale": ["model sale.order (moved to account)"],
                "account": ["model sale.order (moved from sale)"],
            },
        )

    def test_renamed_model_in_same_module(self):
        """A rename reported by apriori is reported from both models."""
        old_records = [record("sale.old", "sale")]
        new_records = [record("sale.new", "sale")]
        self.assertEqual(
            self.run_compare(
                old_records, new_records, renamed_models={"sale.old": "sale.new"}
            ),
            {
                "sale": [
                    "obsolete model sale.old (renamed to sale.new)",
                    "new model sale.new (renamed from sale.old)",
                ],
                "general": [
                    "obsolete model sale.old (renamed to sale.new) [module sale]",
                    "new model sale.new (renamed from sale.old) [module sale]",
                ],
            },
        )

    def test_renamed_model_that_also_moved_module(self):
        """The module move is spelled out on the side that reports the rename."""
        old_records = [record("sale.old", "sale")]
        new_records = [record("sale.new", "account")]
        self.assertEqual(
            self.run_compare(
                old_records, new_records, renamed_models={"sale.old": "sale.new"}
            ),
            {
                "sale": [
                    "obsolete model sale.old (renamed to sale.new in module account)"
                ],
                "account": [
                    "new model sale.new (renamed from sale.old in module sale)"
                ],
                "general": [
                    "obsolete model sale.old (renamed to sale.new) [module sale]",
                    "new model sale.new (renamed from sale.old) [module account]",
                ],
            },
        )

    def test_merged_model(self):
        """A merge is reported as an obsolete source plus a plain new model."""
        old_records = [record("sale.old", "sale")]
        new_records = [record("sale.new", "sale")]
        self.assertEqual(
            self.run_compare(
                old_records, new_records, merged_models={"sale.old": "sale.new"}
            ),
            {
                "sale": [
                    "obsolete model sale.old (merged to sale.new)",
                    "new model sale.new",
                ],
                "general": [
                    "obsolete model sale.old (merged to sale.new) [module sale]",
                    "new model sale.new [module sale]",
                ],
            },
        )

    def test_model_type_is_appended(self):
        """The model type is appended to the module line, not to the general one."""
        old_records = [record("sale.order", "sale")]
        new_records = old_records + [
            record("sale.wizard", "sale", "transient"),
            record("sale.mixin", "sale", "abstract"),
        ]
        self.assertEqual(
            self.run_compare(old_records, new_records),
            {
                "sale": [
                    "new model sale.wizard [transient]",
                    "new model sale.mixin [abstract]",
                ],
                "general": [
                    "new model sale.wizard [module sale]",
                    "new model sale.mixin [module sale]",
                ],
            },
        )

    def test_obsolete_model_type_is_appended(self):
        """An obsolete transient model keeps its type on the module line."""
        old_records = [
            record("sale.order", "sale"),
            record("sale.wizard", "sale", "transient"),
        ]
        new_records = [record("sale.order", "sale")]
        self.assertEqual(
            self.run_compare(old_records, new_records),
            {
                "sale": ["obsolete model sale.wizard [transient]"],
                "general": ["obsolete model sale.wizard [module sale]"],
            },
        )

    def test_module_rename_is_followed(self):
        """A module renamed by apriori is bucketed under its new name.

        The shared model is kept in a module apriori does not rename, so this
        only exercises the bucketing of the obsolete model.
        """
        old_records = [record("sale.order", "account"), record("sale.legacy", "sale")]
        new_records = [record("sale.order", "account")]
        self.assertEqual(
            self.run_compare(
                old_records, new_records, renamed_modules={"sale": "sale_management"}
            ),
            {
                "sale_management": ["obsolete model sale.legacy"],
                "general": ["obsolete model sale.legacy [module sale_management]"],
            },
        )
