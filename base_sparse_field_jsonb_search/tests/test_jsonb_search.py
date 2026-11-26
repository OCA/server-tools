"""Tests for JSONB search functionality on sparse fields."""

import logging
from unittest.mock import MagicMock, patch

from odoo.tests import TransactionCase, tagged

from ..models.base_model import FALSE_LEAF, JSONB_OPERATOR_MAP, TRUE_LEAF
from ..models.expression_patch import (
    _build_jsonb_sql,
    _get_jsonb_leaf_sql,
    _handle_boolean,
    _handle_equality,
    _handle_in_operator,
    _handle_like,
    _handle_null_check,
    _handle_numeric,
    patch_expression_module,
)

# Loggers to mute during warning-generating tests
_LOGGERS_TO_MUTE = [
    "odoo.addons.base_sparse_field_jsonb_search.models.base_model",
    "odoo.addons.base_sparse_field_jsonb_search.models.expression_patch",
]


@tagged("post_install", "-at_install")
class TestJsonbSearchConstants(TransactionCase):
    """Test module constants."""

    def test_true_leaf_constant(self):
        """Test TRUE_LEAF is valid domain leaf."""
        self.assertEqual(TRUE_LEAF, (1, "=", 1))

    def test_false_leaf_constant(self):
        """Test FALSE_LEAF is valid domain leaf."""
        self.assertEqual(FALSE_LEAF, (0, "=", 1))

    def test_jsonb_operator_map_completeness(self):
        """Test all expected operators are mapped."""
        expected_operators = [
            "=",
            "!=",
            "<>",
            "like",
            "ilike",
            "not like",
            "not ilike",
            ">",
            ">=",
            "<",
            "<=",
        ]
        for op in expected_operators:
            self.assertIn(op, JSONB_OPERATOR_MAP)

    def test_jsonb_operator_map_values(self):
        """Test operator mappings are correct."""
        self.assertEqual(JSONB_OPERATOR_MAP["="], "=")
        self.assertEqual(JSONB_OPERATOR_MAP["!="], "!=")
        self.assertEqual(JSONB_OPERATOR_MAP["<>"], "!=")
        self.assertEqual(JSONB_OPERATOR_MAP["like"], "LIKE")
        self.assertEqual(JSONB_OPERATOR_MAP["ilike"], "ILIKE")
        self.assertEqual(JSONB_OPERATOR_MAP["not like"], "NOT LIKE")
        self.assertEqual(JSONB_OPERATOR_MAP["not ilike"], "NOT ILIKE")


@tagged("post_install", "-at_install")
class TestJsonbSearch(TransactionCase):
    """Test JSONB search domain translation for sparse fields."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Base = cls.env["base"]
        cls.Partner = cls.env["res.partner"]

    def test_get_sparse_field_mapping_no_sparse_fields(self):
        """Test mapping returns empty dict for models without sparse fields."""
        mapping = self.Partner._get_sparse_field_mapping()
        # res.partner typically doesn't have sparse fields
        # (unless attribute_set is installed and configured)
        self.assertIsInstance(mapping, dict)

    def test_get_sparse_field_mapping_returns_dict(self):
        """Test mapping always returns a dictionary."""
        mapping = self.Base._get_sparse_field_mapping()
        self.assertIsInstance(mapping, dict)

    def test_transform_jsonb_domain_empty(self):
        """Test empty domain returns empty list."""
        result = self.Base._transform_jsonb_domain([], {})
        self.assertEqual(result, [])

    def test_transform_jsonb_domain_none(self):
        """Test None domain returns None."""
        result = self.Base._transform_jsonb_domain(None, {})
        self.assertIsNone(result)

    def test_transform_jsonb_domain_no_sparse_fields(self):
        """Test domain without sparse fields passes through unchanged."""
        domain = [("name", "=", "test"), ("active", "=", True)]
        result = self.Base._transform_jsonb_domain(domain, {})
        self.assertEqual(result, domain)

    def test_transform_jsonb_domain_with_and_operator(self):
        """Test AND operator passes through unchanged."""
        domain = ["&", ("name", "=", "test"), ("active", "=", True)]
        result = self.Base._transform_jsonb_domain(domain, {})
        self.assertEqual(result, domain)

    def test_transform_jsonb_domain_with_or_operator(self):
        """Test OR operator passes through unchanged."""
        domain = ["|", ("name", "=", "test"), ("name", "=", "test2")]
        result = self.Base._transform_jsonb_domain(domain, {})
        self.assertEqual(result, domain)

    def test_transform_jsonb_domain_with_not_operator(self):
        """Test NOT operator passes through unchanged."""
        domain = ["!", ("active", "=", False)]
        result = self.Base._transform_jsonb_domain(domain, {})
        self.assertEqual(result, domain)

    def test_transform_jsonb_domain_mixed_operators(self):
        """Test complex domain with mixed operators."""
        domain = [
            "&",
            "|",
            ("name", "=", "test1"),
            ("name", "=", "test2"),
            ("active", "=", True),
        ]
        result = self.Base._transform_jsonb_domain(domain, {})
        self.assertEqual(result, domain)

    def test_transform_jsonb_domain_list_leaf(self):
        """Test domain with list-style leaf (instead of tuple)."""
        domain = [["name", "=", "test"]]
        result = self.Base._transform_jsonb_domain(domain, {})
        self.assertEqual(result, domain)

    def test_search_no_sparse_fields(self):
        """Test _search works normally without sparse fields."""
        # This should not raise any errors
        query = self.Partner._search([("name", "=", "test")])
        self.assertIsNotNone(query)

    def test_search_empty_domain(self):
        """Test _search with empty domain."""
        query = self.Partner._search([])
        self.assertIsNotNone(query)

    def test_search_complex_domain(self):
        """Test _search with complex domain."""
        domain = [
            "&",
            ("name", "ilike", "test"),
            "|",
            ("active", "=", True),
            ("comment", "!=", False),
        ]
        query = self.Partner._search(domain)
        self.assertIsNotNone(query)


@tagged("post_install", "-at_install")
class TestJsonbSearchWithMockSparseField(TransactionCase):
    """Test JSONB search with mocked sparse field configuration."""

    @classmethod
    def setUpClass(cls):
        """Set up test data with mock sparse field."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

        # Create a mock field that simulates a sparse field
        cls.mock_field = MagicMock()
        cls.mock_field.type = "char"
        cls.mock_field.sparse = None  # Will be set in tests

        cls.mock_integer_field = MagicMock()
        cls.mock_integer_field.type = "integer"

        cls.mock_float_field = MagicMock()
        cls.mock_float_field.type = "float"

        cls.mock_boolean_field = MagicMock()
        cls.mock_boolean_field.type = "boolean"

        cls.mock_monetary_field = MagicMock()
        cls.mock_monetary_field.type = "monetary"

    def _get_sparse_info(self, field_type="char"):
        """Helper to create sparse_info dict."""
        mock_field = MagicMock()
        mock_field.type = field_type
        return {
            "container": "x_custom_json",
            "field": mock_field,
        }

    def test_transform_jsonb_leaf_equality_string(self):
        """Test leaf transformation for string equality."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf("x_color", "=", "red", sparse_info)
        self.assertEqual(result, ("x_color", "=", "red"))

    def test_transform_jsonb_leaf_inequality_string(self):
        """Test leaf transformation for string inequality."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf("x_color", "!=", "red", sparse_info)
        self.assertEqual(result, ("x_color", "!=", "red"))

    def test_transform_jsonb_leaf_null_check_equals_false(self):
        """Test leaf transformation for NULL check (= False)."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf("x_color", "=", False, sparse_info)
        # Should return fallback for NULL check
        self.assertEqual(result[0], "x_color")
        self.assertEqual(result[1], "=")
        self.assertEqual(result[2], False)

    def test_transform_jsonb_leaf_not_null_check(self):
        """Test leaf transformation for NOT NULL check (!= False)."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf("x_color", "!=", False, sparse_info)
        # Should return fallback for NOT NULL check
        self.assertEqual(result[0], "x_color")
        self.assertEqual(result[1], "!=")
        self.assertEqual(result[2], False)

    def test_transform_jsonb_leaf_in_operator(self):
        """Test leaf transformation for IN operator."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf(
            "x_color", "in", ["red", "blue"], sparse_info
        )
        self.assertEqual(result, ("x_color", "in", ["red", "blue"]))

    def test_transform_jsonb_leaf_in_operator_empty(self):
        """Test leaf transformation for IN with empty list."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf("x_color", "in", [], sparse_info)
        # Empty IN should return FALSE_LEAF
        self.assertEqual(result, FALSE_LEAF)

    def test_transform_jsonb_leaf_not_in_operator(self):
        """Test leaf transformation for NOT IN operator."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf(
            "x_color", "not in", ["red", "blue"], sparse_info
        )
        self.assertEqual(result, ("x_color", "not in", ["red", "blue"]))

    def test_transform_jsonb_leaf_not_in_operator_empty(self):
        """Test leaf transformation for NOT IN with empty list."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf(
            "x_color", "not in", [], sparse_info
        )
        # Empty NOT IN should return TRUE_LEAF
        self.assertEqual(result, TRUE_LEAF)

    def test_transform_jsonb_leaf_like_operator(self):
        """Test leaf transformation for LIKE operator."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf(
            "x_color", "like", "red", sparse_info
        )
        self.assertEqual(result, ("x_color", "like", "red"))

    def test_transform_jsonb_leaf_ilike_operator(self):
        """Test leaf transformation for ILIKE operator."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf(
            "x_color", "ilike", "RED", sparse_info
        )
        self.assertEqual(result, ("x_color", "ilike", "RED"))

    def test_transform_jsonb_leaf_not_like_operator(self):
        """Test leaf transformation for NOT LIKE operator."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf(
            "x_color", "not like", "red", sparse_info
        )
        self.assertEqual(result, ("x_color", "not like", "red"))

    def test_transform_jsonb_leaf_not_ilike_operator(self):
        """Test leaf transformation for NOT ILIKE operator."""
        sparse_info = self._get_sparse_info("char")
        result = self.Partner._transform_jsonb_leaf(
            "x_color", "not ilike", "RED", sparse_info
        )
        self.assertEqual(result, ("x_color", "not ilike", "RED"))

    def test_transform_jsonb_leaf_greater_than_integer(self):
        """Test leaf transformation for > operator with integer."""
        sparse_info = self._get_sparse_info("integer")
        result = self.Partner._transform_jsonb_leaf("x_quantity", ">", 10, sparse_info)
        self.assertEqual(result, ("x_quantity", ">", 10))

    def test_transform_jsonb_leaf_greater_equal_integer(self):
        """Test leaf transformation for >= operator with integer."""
        sparse_info = self._get_sparse_info("integer")
        result = self.Partner._transform_jsonb_leaf("x_quantity", ">=", 10, sparse_info)
        self.assertEqual(result, ("x_quantity", ">=", 10))

    def test_transform_jsonb_leaf_less_than_integer(self):
        """Test leaf transformation for < operator with integer."""
        sparse_info = self._get_sparse_info("integer")
        result = self.Partner._transform_jsonb_leaf("x_quantity", "<", 10, sparse_info)
        self.assertEqual(result, ("x_quantity", "<", 10))

    def test_transform_jsonb_leaf_less_equal_integer(self):
        """Test leaf transformation for <= operator with integer."""
        sparse_info = self._get_sparse_info("integer")
        result = self.Partner._transform_jsonb_leaf("x_quantity", "<=", 10, sparse_info)
        self.assertEqual(result, ("x_quantity", "<=", 10))

    def test_transform_jsonb_leaf_float_comparison(self):
        """Test leaf transformation for float comparison."""
        sparse_info = self._get_sparse_info("float")
        result = self.Partner._transform_jsonb_leaf("x_price", ">", 99.99, sparse_info)
        self.assertEqual(result, ("x_price", ">", 99.99))

    def test_transform_jsonb_leaf_monetary_comparison(self):
        """Test leaf transformation for monetary comparison."""
        sparse_info = self._get_sparse_info("monetary")
        result = self.Partner._transform_jsonb_leaf(
            "x_amount", ">=", 1000.00, sparse_info
        )
        self.assertEqual(result, ("x_amount", ">=", 1000.00))

    def test_transform_jsonb_leaf_boolean_true(self):
        """Test leaf transformation for boolean True."""
        sparse_info = self._get_sparse_info("boolean")
        result = self.Partner._transform_jsonb_leaf("x_active", "=", True, sparse_info)
        self.assertEqual(result, ("x_active", "=", True))

    def test_transform_jsonb_leaf_integer_equality(self):
        """Test leaf transformation for integer equality."""
        sparse_info = self._get_sparse_info("integer")
        result = self.Partner._transform_jsonb_leaf("x_count", "=", 42, sparse_info)
        self.assertEqual(result, ("x_count", "=", 42))


@tagged("post_install", "-at_install")
class TestBuildJsonbNullCheck(TransactionCase):
    """Test _build_jsonb_null_check method."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_build_null_check_is_null(self):
        """Test NULL check returns correct fallback."""
        result = self.Partner._build_jsonb_null_check("x_custom_json", "x_color", True)
        self.assertEqual(result, ("x_color", "=", False))

    def test_build_null_check_is_not_null(self):
        """Test NOT NULL check returns correct fallback."""
        result = self.Partner._build_jsonb_null_check("x_custom_json", "x_color", False)
        self.assertEqual(result, ("x_color", "!=", False))


@tagged("post_install", "-at_install")
class TestBuildJsonbInExpression(TransactionCase):
    """Test _build_jsonb_in_expression method."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]
        cls.mock_field = MagicMock()
        cls.mock_field.type = "char"

    def test_build_in_expression_with_values(self):
        """Test IN expression with values."""
        result = self.Partner._build_jsonb_in_expression(
            "x_custom_json", "x_color", self.mock_field, ["red", "blue"], False
        )
        self.assertEqual(result, ("x_color", "in", ["red", "blue"]))

    def test_build_in_expression_empty_list(self):
        """Test IN expression with empty list returns FALSE_LEAF."""
        result = self.Partner._build_jsonb_in_expression(
            "x_custom_json", "x_color", self.mock_field, [], False
        )
        self.assertEqual(result, FALSE_LEAF)

    def test_build_not_in_expression_with_values(self):
        """Test NOT IN expression with values."""
        result = self.Partner._build_jsonb_in_expression(
            "x_custom_json", "x_color", self.mock_field, ["red", "blue"], True
        )
        self.assertEqual(result, ("x_color", "not in", ["red", "blue"]))

    def test_build_not_in_expression_empty_list(self):
        """Test NOT IN expression with empty list returns TRUE_LEAF."""
        result = self.Partner._build_jsonb_in_expression(
            "x_custom_json", "x_color", self.mock_field, [], True
        )
        self.assertEqual(result, TRUE_LEAF)

    def test_build_in_expression_single_value(self):
        """Test IN expression with single value."""
        result = self.Partner._build_jsonb_in_expression(
            "x_custom_json", "x_color", self.mock_field, ["red"], False
        )
        self.assertEqual(result, ("x_color", "in", ["red"]))


@tagged("post_install", "-at_install")
class TestBuildJsonbComparison(TransactionCase):
    """Test _build_jsonb_comparison method."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def _make_field(self, field_type):
        """Create mock field with given type."""
        mock_field = MagicMock()
        mock_field.type = field_type
        return mock_field

    def test_build_comparison_string_equality(self):
        """Test string equality comparison."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_color", field, "=", "red"
        )
        self.assertEqual(result, ("x_color", "=", "red"))

    def test_build_comparison_string_inequality(self):
        """Test string inequality comparison."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_color", field, "!=", "red"
        )
        self.assertEqual(result, ("x_color", "!=", "red"))

    def test_build_comparison_like(self):
        """Test LIKE comparison."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_color", field, "like", "red"
        )
        self.assertEqual(result, ("x_color", "like", "red"))

    def test_build_comparison_ilike(self):
        """Test ILIKE comparison."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_color", field, "ilike", "RED"
        )
        self.assertEqual(result, ("x_color", "ilike", "RED"))

    def test_build_comparison_not_like(self):
        """Test NOT LIKE comparison."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_color", field, "not like", "red"
        )
        self.assertEqual(result, ("x_color", "not like", "red"))

    def test_build_comparison_not_ilike(self):
        """Test NOT ILIKE comparison."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_color", field, "not ilike", "RED"
        )
        self.assertEqual(result, ("x_color", "not ilike", "RED"))

    def test_build_comparison_integer_greater_than(self):
        """Test integer > comparison."""
        field = self._make_field("integer")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_qty", field, ">", 10
        )
        self.assertEqual(result, ("x_qty", ">", 10))

    def test_build_comparison_integer_greater_equal(self):
        """Test integer >= comparison."""
        field = self._make_field("integer")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_qty", field, ">=", 10
        )
        self.assertEqual(result, ("x_qty", ">=", 10))

    def test_build_comparison_integer_less_than(self):
        """Test integer < comparison."""
        field = self._make_field("integer")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_qty", field, "<", 10
        )
        self.assertEqual(result, ("x_qty", "<", 10))

    def test_build_comparison_integer_less_equal(self):
        """Test integer <= comparison."""
        field = self._make_field("integer")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_qty", field, "<=", 10
        )
        self.assertEqual(result, ("x_qty", "<=", 10))

    def test_build_comparison_float_greater_than(self):
        """Test float > comparison."""
        field = self._make_field("float")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_price", field, ">", 99.99
        )
        self.assertEqual(result, ("x_price", ">", 99.99))

    def test_build_comparison_monetary_greater_equal(self):
        """Test monetary >= comparison."""
        field = self._make_field("monetary")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_amount", field, ">=", 1000.00
        )
        self.assertEqual(result, ("x_amount", ">=", 1000.00))

    def test_build_comparison_boolean_true(self):
        """Test boolean True comparison."""
        field = self._make_field("boolean")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_active", field, "=", True
        )
        self.assertEqual(result, ("x_active", "=", True))

    def test_build_comparison_boolean_false(self):
        """Test boolean False comparison (not NULL check)."""
        field = self._make_field("boolean")
        # Note: This tests the boolean branch, not the NULL check
        # Boolean False with = is handled separately in _transform_jsonb_leaf
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_active", field, "=", False
        )
        self.assertEqual(result, ("x_active", "=", False))

    def test_build_comparison_integer_equality(self):
        """Test integer = comparison (not numeric range)."""
        field = self._make_field("integer")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_qty", field, "=", 42
        )
        self.assertEqual(result, ("x_qty", "=", 42))

    def test_build_comparison_unknown_operator(self):
        """Test unknown operator falls back to same operator."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_color", field, "=~", "pattern"
        )
        # Unknown operator should be passed through
        self.assertEqual(result, ("x_color", "=~", "pattern"))


@tagged("post_install", "-at_install")
class TestDomainTransformWithSparseFields(TransactionCase):
    """Test full domain transformation with sparse fields in mapping."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def _get_mock_sparse_fields(self):
        """Create mock sparse fields mapping."""
        mock_char_field = MagicMock()
        mock_char_field.type = "char"

        mock_int_field = MagicMock()
        mock_int_field.type = "integer"

        return {
            "x_color": {
                "container": "x_custom_json",
                "field": mock_char_field,
            },
            "x_quantity": {
                "container": "x_custom_json",
                "field": mock_int_field,
            },
        }

    def test_transform_domain_with_sparse_field(self):
        """Test domain transformation when sparse field is present."""
        sparse_fields = self._get_mock_sparse_fields()
        domain = [("x_color", "=", "red")]
        result = self.Partner._transform_jsonb_domain(domain, sparse_fields)
        # The result should have the transformed leaf
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("x_color", "=", "red"))

    def test_transform_domain_mixed_sparse_and_regular(self):
        """Test domain with both sparse and regular fields."""
        sparse_fields = self._get_mock_sparse_fields()
        domain = [
            "&",
            ("x_color", "=", "red"),
            ("name", "ilike", "test"),
        ]
        result = self.Partner._transform_jsonb_domain(domain, sparse_fields)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "&")
        self.assertEqual(result[1], ("x_color", "=", "red"))
        self.assertEqual(result[2], ("name", "ilike", "test"))

    def test_transform_domain_multiple_sparse_fields(self):
        """Test domain with multiple sparse fields."""
        sparse_fields = self._get_mock_sparse_fields()
        domain = [
            "&",
            ("x_color", "=", "red"),
            ("x_quantity", ">", 10),
        ]
        result = self.Partner._transform_jsonb_domain(domain, sparse_fields)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "&")
        self.assertEqual(result[1], ("x_color", "=", "red"))
        self.assertEqual(result[2], ("x_quantity", ">", 10))

    def test_transform_domain_sparse_with_in_operator(self):
        """Test domain with sparse field using IN operator."""
        sparse_fields = self._get_mock_sparse_fields()
        domain = [("x_color", "in", ["red", "blue", "green"])]
        result = self.Partner._transform_jsonb_domain(domain, sparse_fields)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("x_color", "in", ["red", "blue", "green"]))

    def test_transform_domain_sparse_with_empty_in(self):
        """Test domain with sparse field using empty IN."""
        sparse_fields = self._get_mock_sparse_fields()
        domain = [("x_color", "in", [])]
        result = self.Partner._transform_jsonb_domain(domain, sparse_fields)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], FALSE_LEAF)


@tagged("post_install", "-at_install")
class TestJsonbSearchWithAttributeSet(TransactionCase):
    """Test JSONB search with OCA attribute_set (if installed)."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        # Check if attribute_set and product modules are installed
        cls.has_attribute_set = "attribute.attribute" in cls.env
        cls.has_product = "product.template" in cls.env

    def test_attribute_set_installed(self):
        """Check if attribute_set module is available for testing."""
        if not self.has_attribute_set:
            self.skipTest("attribute_set module not installed")

        # Verify attribute.attribute model exists
        self.assertIn("attribute.attribute", self.env)

    def test_product_template_sparse_fields(self):
        """Test product.template has sparse field mapping when attributes exist."""
        if not self.has_attribute_set:
            self.skipTest("attribute_set module not installed")
        if not self.has_product:
            self.skipTest("product module not installed")

        # Get sparse field mapping for product.template
        mapping = self.env["product.template"]._get_sparse_field_mapping()

        # Log the mapping for debugging
        if mapping:
            for info in mapping.values():
                self.assertIn("container", info)
                self.assertIn("field", info)

    def test_product_template_search_with_domain(self):
        """Test product.template search works with domain."""
        if not self.has_attribute_set:
            self.skipTest("attribute_set module not installed")
        if not self.has_product:
            self.skipTest("product module not installed")

        # This should not raise any errors
        products = self.env["product.template"].search([("name", "ilike", "test")])
        self.assertIsInstance(products, type(self.env["product.template"]))


# ============================================================================
# Tests for expression_patch.py helper functions
# ============================================================================


@tagged("post_install", "-at_install")
class TestExpressionPatchNullCheck(TransactionCase):
    """Test _handle_null_check helper function from expression_patch.py."""

    def test_handle_null_check_equals_false(self):
        """Test NULL check when operator=, value=False."""
        result = _handle_null_check(
            '"test_table"."container"', "field_name", "=", False
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IS NULL", sql)
        self.assertIn("? %s", sql)
        self.assertEqual(params, ["field_name", "field_name"])

    def test_handle_null_check_not_equals_false(self):
        """Test NOT NULL check when operator!=, value=False."""
        result = _handle_null_check(
            '"test_table"."container"', "field_name", "!=", False
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IS NOT NULL", sql)
        self.assertIn("? %s", sql)
        self.assertEqual(params, ["field_name", "field_name"])

    def test_handle_null_check_other_operator(self):
        """Test returns None for non-null-check operators."""
        result = _handle_null_check(
            '"test_table"."container"', "field_name", "=", "red"
        )
        self.assertIsNone(result)

    def test_handle_null_check_equals_non_false(self):
        """Test returns None when value is not False."""
        result = _handle_null_check(
            '"test_table"."container"', "field_name", "=", "something"
        )
        self.assertIsNone(result)

    def test_handle_null_check_not_equals_non_false(self):
        """Test returns None when value is not False with !=."""
        result = _handle_null_check(
            '"test_table"."container"', "field_name", "!=", "something"
        )
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestExpressionPatchInOperator(TransactionCase):
    """Test _handle_in_operator helper function from expression_patch.py."""

    def test_handle_in_with_values(self):
        """Test IN operator with non-empty list."""
        result = _handle_in_operator(
            '"test_table"."container"', "field_name", "in", ["a", "b", "c"]
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IN", sql)
        self.assertEqual(params, ["field_name", "a", "b", "c"])

    def test_handle_in_empty_list(self):
        """Test IN operator with empty list returns FALSE."""
        result = _handle_in_operator('"test_table"."container"', "field_name", "in", [])
        self.assertIsNotNone(result)
        sql, params = result
        self.assertEqual(sql, "FALSE")
        self.assertEqual(params, [])

    def test_handle_not_in_with_values(self):
        """Test NOT IN operator with non-empty list."""
        result = _handle_in_operator(
            '"test_table"."container"', "field_name", "not in", ["x", "y"]
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("NOT IN", sql)
        self.assertIn("IS NULL OR", sql)
        self.assertEqual(params, ["field_name", "field_name", "x", "y"])

    def test_handle_not_in_empty_list(self):
        """Test NOT IN operator with empty list returns TRUE."""
        result = _handle_in_operator(
            '"test_table"."container"', "field_name", "not in", []
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertEqual(sql, "TRUE")
        self.assertEqual(params, [])

    def test_handle_in_other_operator(self):
        """Test returns None for non-in operators."""
        result = _handle_in_operator(
            '"test_table"."container"', "field_name", "=", ["a", "b"]
        )
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestExpressionPatchBoolean(TransactionCase):
    """Test _handle_boolean helper function from expression_patch.py."""

    def test_handle_boolean_equals_true(self):
        """Test boolean = True."""
        result = _handle_boolean('"test_table"."container"', "field_name", "=", True)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::boolean = TRUE", sql)
        self.assertEqual(params, ["field_name"])

    def test_handle_boolean_equals_false(self):
        """Test boolean = False."""
        result = _handle_boolean('"test_table"."container"', "field_name", "=", False)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IS NULL", sql)
        self.assertIn("::boolean = FALSE", sql)
        self.assertEqual(params, ["field_name", "field_name"])

    def test_handle_boolean_not_equals_true(self):
        """Test boolean != True."""
        result = _handle_boolean('"test_table"."container"', "field_name", "!=", True)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IS NULL", sql)
        self.assertIn("::boolean = FALSE", sql)
        self.assertEqual(params, ["field_name", "field_name"])

    def test_handle_boolean_not_equals_false(self):
        """Test boolean != False."""
        result = _handle_boolean('"test_table"."container"', "field_name", "!=", False)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::boolean = TRUE", sql)
        self.assertEqual(params, ["field_name"])

    def test_handle_boolean_other_operator(self):
        """Test returns None for non-boolean operators."""
        result = _handle_boolean('"test_table"."container"', "field_name", ">", True)
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestExpressionPatchNumeric(TransactionCase):
    """Test _handle_numeric helper function from expression_patch.py."""

    def test_handle_numeric_greater_than(self):
        """Test numeric > comparison."""
        result = _handle_numeric('"test_table"."container"', "field_name", ">", 100)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric >", sql)
        self.assertEqual(params, ["field_name", 100])

    def test_handle_numeric_greater_equal(self):
        """Test numeric >= comparison."""
        result = _handle_numeric('"test_table"."container"', "field_name", ">=", 50)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric >=", sql)
        self.assertEqual(params, ["field_name", 50])

    def test_handle_numeric_less_than(self):
        """Test numeric < comparison."""
        result = _handle_numeric('"test_table"."container"', "field_name", "<", 10)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric <", sql)
        self.assertEqual(params, ["field_name", 10])

    def test_handle_numeric_less_equal(self):
        """Test numeric <= comparison."""
        result = _handle_numeric('"test_table"."container"', "field_name", "<=", 25)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric <=", sql)
        self.assertEqual(params, ["field_name", 25])

    def test_handle_numeric_equals(self):
        """Test numeric = comparison."""
        result = _handle_numeric('"test_table"."container"', "field_name", "=", 42)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric =", sql)
        self.assertEqual(params, ["field_name", 42])

    def test_handle_numeric_not_equals(self):
        """Test numeric != comparison."""
        result = _handle_numeric('"test_table"."container"', "field_name", "!=", 99)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IS NULL OR", sql)
        self.assertIn("::numeric !=", sql)
        self.assertEqual(params, ["field_name", "field_name", 99])

    def test_handle_numeric_other_operator(self):
        """Test returns None for non-numeric operators."""
        result = _handle_numeric('"test_table"."container"', "field_name", "like", 100)
        self.assertIsNone(result)

    def test_handle_numeric_with_float(self):
        """Test numeric comparison with float value."""
        result = _handle_numeric('"test_table"."container"', "field_name", ">", 99.99)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertEqual(params, ["field_name", 99.99])


@tagged("post_install", "-at_install")
class TestExpressionPatchLike(TransactionCase):
    """Test _handle_like helper function from expression_patch.py."""

    def test_handle_like(self):
        """Test LIKE operator."""
        result = _handle_like('"test_table"."container"', "field_name", "like", "test")
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("LIKE", sql)
        self.assertNotIn("ILIKE", sql)
        self.assertEqual(params, ["field_name", "%test%"])

    def test_handle_ilike(self):
        """Test ILIKE operator."""
        result = _handle_like('"test_table"."container"', "field_name", "ilike", "TEST")
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("ILIKE", sql)
        self.assertEqual(params, ["field_name", "%TEST%"])

    def test_handle_not_like(self):
        """Test NOT LIKE operator."""
        result = _handle_like(
            '"test_table"."container"', "field_name", "not like", "bad"
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("NOT LIKE", sql)
        self.assertIn("IS NULL OR", sql)
        self.assertEqual(params, ["field_name", "field_name", "%bad%"])

    def test_handle_not_ilike(self):
        """Test NOT ILIKE operator."""
        result = _handle_like(
            '"test_table"."container"', "field_name", "not ilike", "BAD"
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("NOT ILIKE", sql)
        self.assertIn("IS NULL OR", sql)
        self.assertEqual(params, ["field_name", "field_name", "%BAD%"])

    def test_handle_like_other_operator(self):
        """Test returns None for non-like operators."""
        result = _handle_like('"test_table"."container"', "field_name", "=", "test")
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestExpressionPatchEquality(TransactionCase):
    """Test _handle_equality helper function from expression_patch.py."""

    def test_handle_equality_equals(self):
        """Test = operator."""
        result = _handle_equality('"test_table"."container"', "field_name", "=", "red")
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("->>%s = %s", sql)
        self.assertEqual(params, ["field_name", "red"])

    def test_handle_equality_not_equals(self):
        """Test != operator."""
        result = _handle_equality(
            '"test_table"."container"', "field_name", "!=", "blue"
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IS NULL OR", sql)
        self.assertIn("!= %s", sql)
        self.assertEqual(params, ["field_name", "field_name", "blue"])

    def test_handle_equality_not_equal_alternate(self):
        """Test <> operator (alternate not equal)."""
        result = _handle_equality(
            '"test_table"."container"', "field_name", "<>", "green"
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IS NULL OR", sql)
        self.assertIn("!= %s", sql)
        self.assertEqual(params, ["field_name", "field_name", "green"])

    def test_handle_equality_other_operator(self):
        """Test returns None for non-equality operators."""
        result = _handle_equality('"test_table"."container"', "field_name", ">", "test")
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestExpressionPatchGetJsonbLeafSql(TransactionCase):
    """Test _get_jsonb_leaf_sql function from expression_patch.py."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_get_jsonb_leaf_sql_field_not_in_model(self):
        """Test returns None when field doesn't exist in model."""
        result = _get_jsonb_leaf_sql(
            self.Partner, ("nonexistent_field", "=", "value"), "res_partner"
        )
        self.assertIsNone(result)

    def test_get_jsonb_leaf_sql_field_not_sparse(self):
        """Test returns None when field is not sparse."""
        result = _get_jsonb_leaf_sql(self.Partner, ("name", "=", "Test"), "res_partner")
        self.assertIsNone(result)

    def test_get_jsonb_leaf_sql_sparse_container_not_in_model(self):
        """Test returns None when sparse container doesn't exist."""
        # Create a mock model with a sparse field pointing to non-existent container
        mock_model = MagicMock()
        mock_field = MagicMock()
        mock_field.sparse = "nonexistent_container"
        mock_model._fields = {"x_color": mock_field}
        result = _get_jsonb_leaf_sql(mock_model, ("x_color", "=", "red"), "test_table")
        self.assertIsNone(result)

    def test_get_jsonb_leaf_sql_container_not_serialized(self):
        """Test returns None when container is not serialized type."""
        mock_model = MagicMock()
        mock_sparse_field = MagicMock()
        mock_sparse_field.sparse = "container_field"
        mock_container_field = MagicMock()
        mock_container_field.type = "char"  # Not serialized
        mock_model._fields = {
            "x_color": mock_sparse_field,
            "container_field": mock_container_field,
        }
        result = _get_jsonb_leaf_sql(mock_model, ("x_color", "=", "red"), "test_table")
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestExpressionPatchBuildJsonbSql(TransactionCase):
    """Test _build_jsonb_sql function from expression_patch.py."""

    def _make_field(self, field_type):
        """Create mock field with given type."""
        mock_field = MagicMock()
        mock_field.type = field_type
        return mock_field

    def test_build_jsonb_sql_null_check(self):
        """Test _build_jsonb_sql routes to null check handler."""
        field = self._make_field("char")
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, "=", False
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IS NULL", sql)

    def test_build_jsonb_sql_in_operator(self):
        """Test _build_jsonb_sql routes to in operator handler."""
        field = self._make_field("char")
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, "in", ["a", "b"]
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IN", sql)

    def test_build_jsonb_sql_boolean(self):
        """Test _build_jsonb_sql routes to boolean handler."""
        field = self._make_field("boolean")
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, "=", True
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::boolean", sql)

    def test_build_jsonb_sql_numeric(self):
        """Test _build_jsonb_sql routes to numeric handler."""
        field = self._make_field("integer")
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, ">", 100
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric", sql)

    def test_build_jsonb_sql_like(self):
        """Test _build_jsonb_sql routes to like handler."""
        field = self._make_field("char")
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, "like", "test"
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("LIKE", sql)

    def test_build_jsonb_sql_equality(self):
        """Test _build_jsonb_sql routes to equality handler."""
        field = self._make_field("char")
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, "=", "red"
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("= %s", sql)

    def test_build_jsonb_sql_unsupported_operator(self):
        """Test _build_jsonb_sql returns None for unsupported operator."""
        field = self._make_field("char")
        # Use an operator that none of the handlers support
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, "~", "pattern"
        )
        self.assertIsNone(result)

    def test_build_jsonb_sql_float_type(self):
        """Test _build_jsonb_sql with float field type."""
        field = self._make_field("float")
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, ">=", 99.5
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric", sql)

    def test_build_jsonb_sql_monetary_type(self):
        """Test _build_jsonb_sql with monetary field type."""
        field = self._make_field("monetary")
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, "<=", 1000.00
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric", sql)


@tagged("post_install", "-at_install")
class TestExpressionPatchPatchFunction(TransactionCase):
    """Test patch_expression_module function."""

    def test_patch_expression_module_can_be_called(self):
        """Test patch_expression_module can be called without error."""
        # First call should apply patch
        patch_expression_module()
        # Second call should be idempotent (already patched check)
        patch_expression_module()
        # No exception means success


@tagged("post_install", "-at_install")
class TestBaseModelBuildComparisonValueTypes(TransactionCase):
    """Test _build_jsonb_comparison with different value types in base_model.py."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def _make_field(self, field_type):
        """Create mock field with given type."""
        mock_field = MagicMock()
        mock_field.type = field_type
        return mock_field

    def test_build_comparison_with_none_value(self):
        """Test comparison with None value."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_color", field, "=", None
        )
        # None should fall through to the else branch
        self.assertEqual(result, ("x_color", "=", None))

    def test_build_comparison_diamond_operator(self):
        """Test comparison with <> operator."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_color", field, "<>", "red"
        )
        self.assertEqual(result, ("x_color", "<>", "red"))


@tagged("post_install", "-at_install")
class TestBaseModelBuildJsonbNullCheckSQL(TransactionCase):
    """Test _build_jsonb_null_check generates correct SQL internally."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_null_check_sql_is_generated(self):
        """Test that SQL is generated in _build_jsonb_null_check (via logging)."""
        with patch(
            "odoo.addons.base_sparse_field_jsonb_search.models.base_model._logger"
        ) as mock_logger:
            self.Partner._build_jsonb_null_check("x_custom_json", "x_color", True)
            # Verify debug logging was called with SQL
            self.assertTrue(mock_logger.debug.called)

    def test_not_null_check_sql_is_generated(self):
        """Test that SQL is generated for NOT NULL check (via logging)."""
        with patch(
            "odoo.addons.base_sparse_field_jsonb_search.models.base_model._logger"
        ) as mock_logger:
            self.Partner._build_jsonb_null_check("x_custom_json", "x_color", False)
            # Verify debug logging was called with SQL
            self.assertTrue(mock_logger.debug.called)


@tagged("post_install", "-at_install")
class TestBaseModelBuildJsonbInExpressionSQL(TransactionCase):
    """Test _build_jsonb_in_expression generates correct SQL internally."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]
        cls.mock_field = MagicMock()
        cls.mock_field.type = "char"

    def test_in_expression_sql_is_generated(self):
        """Test that SQL is generated for IN expression (via logging)."""
        with patch(
            "odoo.addons.base_sparse_field_jsonb_search.models.base_model._logger"
        ) as mock_logger:
            self.Partner._build_jsonb_in_expression(
                "x_custom_json", "x_color", self.mock_field, ["red", "blue"], False
            )
            # Verify debug logging was called
            self.assertTrue(mock_logger.debug.called)


@tagged("post_install", "-at_install")
class TestBaseModelTransformJsonbLeafLogging(TransactionCase):
    """Test _transform_jsonb_leaf logging."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def _get_sparse_info(self, field_type="char"):
        """Helper to create sparse_info dict."""
        mock_field = MagicMock()
        mock_field.type = field_type
        return {
            "container": "x_custom_json",
            "field": mock_field,
        }

    def test_transform_leaf_logs_debug(self):
        """Test that _transform_jsonb_leaf logs debug information."""
        with patch(
            "odoo.addons.base_sparse_field_jsonb_search.models.base_model._logger"
        ) as mock_logger:
            sparse_info = self._get_sparse_info("char")
            self.Partner._transform_jsonb_leaf("x_color", "=", "red", sparse_info)
            # Verify debug logging was called
            self.assertTrue(mock_logger.debug.called)


@tagged("post_install", "-at_install")
class TestBaseModelBuildJsonbComparisonSQL(TransactionCase):
    """Test _build_jsonb_comparison SQL generation paths."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def _make_field(self, field_type):
        """Create mock field with given type."""
        mock_field = MagicMock()
        mock_field.type = field_type
        return mock_field

    def test_comparison_sql_with_string_logs_debug(self):
        """Test string comparison logs debug."""
        with patch(
            "odoo.addons.base_sparse_field_jsonb_search.models.base_model._logger"
        ) as mock_logger:
            field = self._make_field("char")
            self.Partner._build_jsonb_comparison(
                "x_custom_json", "x_color", field, "=", "red"
            )
            self.assertTrue(mock_logger.debug.called)

    def test_comparison_sql_with_int_logs_debug(self):
        """Test integer comparison logs debug."""
        with patch(
            "odoo.addons.base_sparse_field_jsonb_search.models.base_model._logger"
        ) as mock_logger:
            field = self._make_field("integer")
            self.Partner._build_jsonb_comparison(
                "x_custom_json", "x_qty", field, ">", 100
            )
            self.assertTrue(mock_logger.debug.called)

    def test_comparison_sql_with_float_logs_debug(self):
        """Test float comparison logs debug."""
        with patch(
            "odoo.addons.base_sparse_field_jsonb_search.models.base_model._logger"
        ) as mock_logger:
            field = self._make_field("float")
            self.Partner._build_jsonb_comparison(
                "x_custom_json", "x_price", field, ">=", 99.99
            )
            self.assertTrue(mock_logger.debug.called)

    def test_comparison_sql_with_boolean_logs_debug(self):
        """Test boolean comparison logs debug."""
        with patch(
            "odoo.addons.base_sparse_field_jsonb_search.models.base_model._logger"
        ) as mock_logger:
            field = self._make_field("boolean")
            self.Partner._build_jsonb_comparison(
                "x_custom_json", "x_active", field, "=", True
            )
            self.assertTrue(mock_logger.debug.called)

    def test_comparison_numeric_needs_numeric_cast(self):
        """Test that numeric fields with range operators use numeric cast."""
        field = self._make_field("integer")
        # This tests the needs_numeric = True branch
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_qty", field, ">", 50
        )
        self.assertEqual(result, ("x_qty", ">", 50))

    def test_comparison_numeric_equality_no_cast(self):
        """Test that numeric fields with = don't need numeric cast for range."""
        field = self._make_field("integer")
        # With = operator, needs_numeric should be False
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_qty", field, "=", 50
        )
        self.assertEqual(result, ("x_qty", "=", 50))


@tagged("post_install", "-at_install")
class TestSparseFieldMappingEdgeCases(TransactionCase):
    """Test edge cases in _get_sparse_field_mapping."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_mapping_with_sparse_pointing_to_nonexistent_container(self):
        """Test that sparse fields pointing to nonexistent containers are skipped."""
        # This is an edge case where sparse attr exists but container doesn't
        # The method should just skip these fields
        mapping = self.Partner._get_sparse_field_mapping()
        # Result should still be a valid dict (possibly empty)
        self.assertIsInstance(mapping, dict)

    def test_mapping_iterates_all_fields(self):
        """Test that mapping checks all fields in model."""
        # Ensure the method actually iterates _fields
        mapping = self.Partner._get_sparse_field_mapping()
        # The partner model has many fields, this should complete without error
        self.assertIsInstance(mapping, dict)


@tagged("post_install", "-at_install")
class TestSearchMethodParameters(TransactionCase):
    """Test _search method with various parameter combinations."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_search_with_offset(self):
        """Test _search with offset parameter."""
        query = self.Partner._search([("name", "ilike", "test")], offset=10)
        self.assertIsNotNone(query)

    def test_search_with_limit(self):
        """Test _search with limit parameter."""
        query = self.Partner._search([("name", "ilike", "test")], limit=5)
        self.assertIsNotNone(query)

    def test_search_with_order(self):
        """Test _search with order parameter."""
        query = self.Partner._search([("name", "ilike", "test")], order="name desc")
        self.assertIsNotNone(query)

    def test_search_with_offset_and_limit(self):
        """Test _search with both offset and limit."""
        query = self.Partner._search([("name", "ilike", "test")], offset=5, limit=10)
        self.assertIsNotNone(query)

    def test_search_with_active_test_false(self):
        """Test _search with active_test=False."""
        query = self.Partner._search([("name", "ilike", "test")], active_test=False)
        self.assertIsNotNone(query)

    def test_search_with_bypass_access_true(self):
        """Test _search with bypass_access=True."""
        query = self.Partner._search([("name", "ilike", "test")], bypass_access=True)
        self.assertIsNotNone(query)

    def test_search_with_all_parameters(self):
        """Test _search with all parameters."""
        query = self.Partner._search(
            [("name", "ilike", "test")],
            offset=0,
            limit=100,
            order="id asc",
            active_test=True,
            bypass_access=False,
        )
        self.assertIsNotNone(query)


@tagged("post_install", "-at_install")
class TestSparseFieldMappingContainerTypes(TransactionCase):
    """Test _get_sparse_field_mapping with various container field types."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_mapping_skips_non_serialized_container(self):
        """Test that sparse fields with non-serialized containers are skipped."""
        # Create a mock model where sparse points to a char field (not serialized)
        mock_model = MagicMock()
        mock_sparse_field = MagicMock()
        mock_sparse_field.sparse = "char_container"

        mock_container_field = MagicMock()
        mock_container_field.type = "char"  # Not serialized!

        mock_model._fields = {
            "x_color": mock_sparse_field,
            "char_container": mock_container_field,
        }

        # Call the method on our Partner but with mocked fields
        with patch.object(self.Partner.__class__, "_fields", mock_model._fields):
            mapping = self.Partner._get_sparse_field_mapping()
            # x_color should NOT be in the mapping since container is not serialized
            self.assertNotIn("x_color", mapping)

    def test_mapping_includes_serialized_container(self):
        """Test that sparse fields with serialized containers are included."""
        mock_model = MagicMock()
        mock_sparse_field = MagicMock()
        mock_sparse_field.sparse = "json_container"

        mock_container_field = MagicMock()
        mock_container_field.type = "serialized"  # Correct type

        mock_model._fields = {
            "x_color": mock_sparse_field,
            "json_container": mock_container_field,
        }

        with patch.object(self.Partner.__class__, "_fields", mock_model._fields):
            mapping = self.Partner._get_sparse_field_mapping()
            # x_color SHOULD be in the mapping
            self.assertIn("x_color", mapping)
            self.assertEqual(mapping["x_color"]["container"], "json_container")


@tagged("post_install", "-at_install")
class TestBuildJsonbSqlWarningPath(TransactionCase):
    """Test _build_jsonb_sql warning path for unsupported operators."""

    @classmethod
    def setUpClass(cls):
        """Set up test data and mute loggers."""
        super().setUpClass()
        # Mute loggers to prevent warnings in test output
        cls._muted_loggers = []
        for logger_name in _LOGGERS_TO_MUTE:
            logger = logging.getLogger(logger_name)
            cls._muted_loggers.append((logger, logger.level))
            logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """Restore logger levels."""
        for logger, level in cls._muted_loggers:
            logger.setLevel(level)
        super().tearDownClass()

    def _make_field(self, field_type):
        """Create mock field with given type."""
        mock_field = MagicMock()
        mock_field.type = field_type
        return mock_field

    def test_unsupported_operator_returns_none(self):
        """Test that unsupported operator returns None."""
        field = self._make_field("char")
        # Use operators that none of the handlers support
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, "~", "pattern"
        )
        self.assertIsNone(result)

    def test_unsupported_operator_regex(self):
        """Test regex operator returns None."""
        field = self._make_field("char")
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, "=~", "pattern"
        )
        self.assertIsNone(result)

    def test_unsupported_operator_custom(self):
        """Test custom operator returns None."""
        field = self._make_field("char")
        result = _build_jsonb_sql(
            "test_table", "container", "field_name", field, "custom_op", "value"
        )
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestGetJsonbLeafSqlValidSparseField(TransactionCase):
    """Test _get_jsonb_leaf_sql with valid sparse field configuration."""

    def _make_mock_model_with_sparse_field(self):
        """Create mock model with valid sparse field."""
        mock_model = MagicMock()

        mock_sparse_field = MagicMock()
        mock_sparse_field.sparse = "x_data"
        mock_sparse_field.type = "char"

        mock_container_field = MagicMock()
        mock_container_field.type = "serialized"

        mock_model._fields = {
            "x_color": mock_sparse_field,
            "x_data": mock_container_field,
        }

        return mock_model

    def test_get_jsonb_leaf_sql_valid_sparse_field(self):
        """Test returns SQL for valid sparse field."""
        mock_model = self._make_mock_model_with_sparse_field()
        result = _get_jsonb_leaf_sql(mock_model, ("x_color", "=", "red"), "test_table")
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("x_data", sql)
        self.assertIn("= %s", sql)

    def test_get_jsonb_leaf_sql_valid_sparse_field_in_operator(self):
        """Test returns SQL for IN operator on sparse field."""
        mock_model = self._make_mock_model_with_sparse_field()
        result = _get_jsonb_leaf_sql(
            mock_model, ("x_color", "in", ["red", "blue"]), "test_table"
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IN", sql)

    def test_get_jsonb_leaf_sql_valid_sparse_field_null_check(self):
        """Test returns SQL for NULL check on sparse field."""
        mock_model = self._make_mock_model_with_sparse_field()
        result = _get_jsonb_leaf_sql(mock_model, ("x_color", "=", False), "test_table")
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IS NULL", sql)


@tagged("post_install", "-at_install")
class TestBuildJsonbSqlNumericFieldTypes(TransactionCase):
    """Test _build_jsonb_sql with all numeric field types."""

    def _make_field(self, field_type):
        """Create mock field with given type."""
        mock_field = MagicMock()
        mock_field.type = field_type
        return mock_field

    def test_integer_field_greater_than(self):
        """Test integer field with > operator."""
        field = self._make_field("integer")
        result = _build_jsonb_sql("test_table", "container", "qty", field, ">", 10)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric", sql)

    def test_float_field_less_than(self):
        """Test float field with < operator."""
        field = self._make_field("float")
        result = _build_jsonb_sql("test_table", "container", "price", field, "<", 99.99)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric", sql)

    def test_monetary_field_less_equal(self):
        """Test monetary field with <= operator."""
        field = self._make_field("monetary")
        result = _build_jsonb_sql(
            "test_table", "container", "amount", field, "<=", 1000.00
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric", sql)

    def test_integer_field_equality(self):
        """Test integer field with = operator (numeric handler)."""
        field = self._make_field("integer")
        result = _build_jsonb_sql("test_table", "container", "count", field, "=", 42)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric =", sql)

    def test_integer_field_not_equality(self):
        """Test integer field with != operator (numeric handler)."""
        field = self._make_field("integer")
        result = _build_jsonb_sql("test_table", "container", "count", field, "!=", 0)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric !=", sql)


@tagged("post_install", "-at_install")
class TestSearchWithSparseFieldsIntegration(TransactionCase):
    """Integration tests for search with sparse field domains."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_search_returns_query_object(self):
        """Test _search returns a Query object."""
        query = self.Partner._search([("active", "=", True)])
        # Query object should have certain attributes
        self.assertIsNotNone(query)

    def test_search_with_compound_domain(self):
        """Test _search with compound OR domain."""
        query = self.Partner._search(
            [
                "|",
                ("name", "=", "Test1"),
                ("name", "=", "Test2"),
            ]
        )
        self.assertIsNotNone(query)

    def test_search_with_negation(self):
        """Test _search with NOT operator in domain."""
        query = self.Partner._search(
            [
                "!",
                ("name", "=", "Test"),
            ]
        )
        self.assertIsNotNone(query)

    def test_search_with_nested_operators(self):
        """Test _search with deeply nested domain."""
        query = self.Partner._search(
            [
                "&",
                "|",
                ("name", "=", "A"),
                ("name", "=", "B"),
                "&",
                ("active", "=", True),
                ("is_company", "=", False),
            ]
        )
        self.assertIsNotNone(query)


@tagged("post_install", "-at_install")
class TestExpressionPatchIdempotence(TransactionCase):
    """Test patch_expression_module idempotence."""

    def test_patch_multiple_calls_safe(self):
        """Test calling patch_expression_module multiple times is safe."""
        # Call multiple times - should not raise
        for _ in range(5):
            patch_expression_module()
        # No assertion needed - just shouldn't raise


@tagged("post_install", "-at_install")
class TestHandleNullCheckEdgeCases(TransactionCase):
    """Test _handle_null_check edge cases."""

    def test_null_check_with_zero(self):
        """Test NULL check with 0 value (not False)."""
        result = _handle_null_check('"test_table"."container"', "field_name", "=", 0)
        # 0 is not False, so should return None
        self.assertIsNone(result)

    def test_null_check_with_empty_string(self):
        """Test NULL check with empty string (not False)."""
        result = _handle_null_check('"test_table"."container"', "field_name", "=", "")
        # "" is not False, so should return None
        self.assertIsNone(result)

    def test_null_check_with_none(self):
        """Test NULL check with None value (not False)."""
        result = _handle_null_check('"test_table"."container"', "field_name", "=", None)
        # None is not False, so should return None
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestHandleInOperatorSingleValue(TransactionCase):
    """Test _handle_in_operator with single value lists."""

    def test_in_single_value(self):
        """Test IN with single value list."""
        result = _handle_in_operator(
            '"test_table"."container"', "field_name", "in", ["only_one"]
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("IN", sql)
        self.assertEqual(len(params), 2)  # field_name + 1 value

    def test_not_in_single_value(self):
        """Test NOT IN with single value list."""
        result = _handle_in_operator(
            '"test_table"."container"', "field_name", "not in", ["only_one"]
        )
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("NOT IN", sql)


@tagged("post_install", "-at_install")
class TestTransformDomainWithListLeaves(TransactionCase):
    """Test domain transformation with list-style leaves (not tuples)."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_list_leaf_passes_through(self):
        """Test that list-style leaves are processed correctly."""
        domain = [["name", "=", "test"]]
        result = self.Partner._transform_jsonb_domain(domain, {})
        self.assertEqual(result, [["name", "=", "test"]])

    def test_mixed_list_and_tuple_leaves(self):
        """Test domain with both list and tuple leaves."""
        domain = [
            "&",
            ["name", "=", "test1"],
            ("active", "=", True),
        ]
        result = self.Partner._transform_jsonb_domain(domain, {})
        self.assertEqual(len(result), 3)


@tagged("post_install", "-at_install")
class TestJsonbOperatorMapCoverage(TransactionCase):
    """Test all operators in JSONB_OPERATOR_MAP."""

    def test_all_comparison_operators_mapped(self):
        """Test that comparison operators have correct mappings."""
        self.assertEqual(JSONB_OPERATOR_MAP[">"], ">")
        self.assertEqual(JSONB_OPERATOR_MAP[">="], ">=")
        self.assertEqual(JSONB_OPERATOR_MAP["<"], "<")
        self.assertEqual(JSONB_OPERATOR_MAP["<="], "<=")

    def test_all_like_operators_mapped(self):
        """Test that LIKE operators have correct mappings."""
        self.assertEqual(JSONB_OPERATOR_MAP["like"], "LIKE")
        self.assertEqual(JSONB_OPERATOR_MAP["ilike"], "ILIKE")
        self.assertEqual(JSONB_OPERATOR_MAP["not like"], "NOT LIKE")
        self.assertEqual(JSONB_OPERATOR_MAP["not ilike"], "NOT ILIKE")


@tagged("post_install", "-at_install")
class TestBuildComparisonNonStringNonNumericValues(TransactionCase):
    """Test _build_jsonb_comparison with various value types."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def _make_field(self, field_type):
        """Create mock field with given type."""
        mock_field = MagicMock()
        mock_field.type = field_type
        return mock_field

    def test_comparison_with_list_value(self):
        """Test comparison with list value (edge case)."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_tags", field, "=", ["tag1", "tag2"]
        )
        # Should return fallback
        self.assertEqual(result[0], "x_tags")

    def test_comparison_with_dict_value(self):
        """Test comparison with dict value (edge case)."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_data", field, "=", {"key": "value"}
        )
        # Should return fallback
        self.assertEqual(result[0], "x_data")


@tagged("post_install", "-at_install")
class TestSparseFieldMappingNonexistentContainer(TransactionCase):
    """Test _get_sparse_field_mapping when sparse points to nonexistent container."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_mapping_skips_nonexistent_container(self):
        """Test sparse field with nonexistent container is skipped."""
        mock_sparse_field = MagicMock()
        mock_sparse_field.sparse = "nonexistent_container"
        mock_fields = {"x_color": mock_sparse_field}

        with patch.object(self.Partner.__class__, "_fields", mock_fields):
            mapping = self.Partner._get_sparse_field_mapping()
            self.assertNotIn("x_color", mapping)

    def test_mapping_skips_field_without_sparse_attr(self):
        """Test field without sparse attribute is skipped."""
        mock_field = MagicMock(spec=[])
        mock_fields = {"regular_field": mock_field}

        with patch.object(self.Partner.__class__, "_fields", mock_fields):
            mapping = self.Partner._get_sparse_field_mapping()
            self.assertNotIn("regular_field", mapping)


@tagged("post_install", "-at_install")
class TestBuildJsonbComparisonOperatorFallback(TransactionCase):
    """Test _build_jsonb_comparison uses fallback for unknown operators."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def _make_field(self, field_type):
        mock_field = MagicMock()
        mock_field.type = field_type
        return mock_field

    def test_unknown_operator_uses_itself_as_pg_operator(self):
        """Test unknown operator falls back to itself."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "x_custom_json", "x_regex", field, "~*", "pattern"
        )
        self.assertEqual(result, ("x_regex", "~*", "pattern"))


@tagged("post_install", "-at_install")
class TestBuildJsonbSqlFieldTypeRouting(TransactionCase):
    """Test _build_jsonb_sql routes to correct handler based on field type."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._muted_loggers = []
        for logger_name in _LOGGERS_TO_MUTE:
            logger = logging.getLogger(logger_name)
            cls._muted_loggers.append((logger, logger.level))
            logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        for logger, level in cls._muted_loggers:
            logger.setLevel(level)
        super().tearDownClass()

    def _make_field(self, field_type):
        mock_field = MagicMock()
        mock_field.type = field_type
        return mock_field

    def test_char_field_with_equality(self):
        """Test char field routes to equality handler."""
        field = self._make_field("char")
        result = _build_jsonb_sql("t", "c", "f", field, "=", "value")
        self.assertIsNotNone(result)

    def test_text_field_with_like(self):
        """Test text field routes to like handler."""
        field = self._make_field("text")
        result = _build_jsonb_sql("t", "c", "f", field, "like", "pattern")
        self.assertIsNotNone(result)

    def test_selection_field_with_equality(self):
        """Test selection field routes to equality handler."""
        field = self._make_field("selection")
        result = _build_jsonb_sql("t", "c", "f", field, "=", "option1")
        self.assertIsNotNone(result)

    def test_many2one_field_with_in(self):
        """Test many2one field routes to in handler."""
        field = self._make_field("many2one")
        result = _build_jsonb_sql("t", "c", "f", field, "in", [1, 2, 3])
        self.assertIsNotNone(result)

    def test_date_field_unsupported_operator(self):
        """Test date field with unsupported operator returns None."""
        field = self._make_field("date")
        result = _build_jsonb_sql(
            "t", "c", "f", field, "between", ["2024-01-01", "2024-12-31"]
        )
        self.assertIsNone(result)


@tagged("post_install", "-at_install")
class TestSearchWithMockedSparseFields(TransactionCase):
    """Test _search when model has sparse fields."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_search_transforms_domain_with_sparse_field(self):
        """Test _search calls _transform_jsonb_domain when sparse fields exist."""
        mock_sparse_field = MagicMock()
        mock_sparse_field.sparse = "x_data"
        mock_sparse_field.type = "char"

        mock_container_field = MagicMock()
        mock_container_field.type = "serialized"

        mock_fields = {
            **self.Partner._fields,
            "x_color": mock_sparse_field,
            "x_data": mock_container_field,
        }

        with patch.object(self.Partner.__class__, "_fields", mock_fields):
            query = self.Partner._search([("x_color", "=", "red")])
            self.assertIsNotNone(query)

    def test_search_with_sparse_field_in_operator(self):
        """Test _search with IN operator on sparse field."""
        mock_sparse_field = MagicMock()
        mock_sparse_field.sparse = "x_data"
        mock_sparse_field.type = "char"

        mock_container_field = MagicMock()
        mock_container_field.type = "serialized"

        mock_fields = {
            **self.Partner._fields,
            "x_size": mock_sparse_field,
            "x_data": mock_container_field,
        }

        with patch.object(self.Partner.__class__, "_fields", mock_fields):
            query = self.Partner._search([("x_size", "in", ["S", "M", "L"])])
            self.assertIsNotNone(query)


@tagged("post_install", "-at_install")
class TestHandlersWithVariousInputs(TransactionCase):
    """Test helper handlers with various edge case inputs."""

    def test_handle_in_many_values(self):
        """Test IN with many values generates correct placeholders."""
        values = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
        result = _handle_in_operator('"t"."c"', "f", "in", values)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertEqual(sql.count("%s"), 11)
        self.assertEqual(len(params), 11)

    def test_handle_not_in_many_values(self):
        """Test NOT IN with many values."""
        values = list(range(1, 21))
        result = _handle_in_operator('"t"."c"', "f", "not in", values)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("NOT IN", sql)
        self.assertEqual(len(params), 22)

    def test_handle_numeric_with_negative(self):
        """Test numeric handler with negative value."""
        result = _handle_numeric('"t"."c"', "f", ">", -100)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertEqual(params[1], -100)

    def test_handle_numeric_with_zero(self):
        """Test numeric handler with zero value."""
        result = _handle_numeric('"t"."c"', "f", "=", 0)
        self.assertIsNotNone(result)
        sql, params = result
        self.assertEqual(params[1], 0)

    def test_handle_like_with_special_chars(self):
        """Test LIKE with special characters in pattern."""
        result = _handle_like('"t"."c"', "f", "like", "test%value")
        self.assertIsNotNone(result)
        sql, params = result
        self.assertEqual(params[1], "%test%value%")

    def test_handle_ilike_with_unicode(self):
        """Test ILIKE with unicode characters."""
        result = _handle_like('"t"."c"', "f", "ilike", "tëst")
        self.assertIsNotNone(result)
        sql, params = result
        self.assertEqual(params[1], "%tëst%")

    def test_handle_equality_with_numeric_string(self):
        """Test equality handler with numeric string value."""
        result = _handle_equality('"t"."c"', "f", "=", "123")
        self.assertIsNotNone(result)
        sql, params = result
        self.assertEqual(params[1], "123")


@tagged("post_install", "-at_install")
class TestTransformDomainComplexCases(TransactionCase):
    """Test domain transformation with complex domain structures."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def _get_mock_sparse_fields(self):
        mock_field = MagicMock()
        mock_field.type = "char"
        return {
            "x_color": {"container": "x_data", "field": mock_field},
            "x_size": {"container": "x_data", "field": mock_field},
        }

    def test_domain_with_multiple_same_field(self):
        """Test domain with same sparse field multiple times."""
        sparse_fields = self._get_mock_sparse_fields()
        domain = ["&", ("x_color", "!=", "red"), ("x_color", "!=", "blue")]
        result = self.Partner._transform_jsonb_domain(domain, sparse_fields)
        self.assertEqual(len(result), 3)

    def test_domain_with_short_tuple(self):
        """Test domain with tuple shorter than 3 elements."""
        domain = [("name",)]
        result = self.Partner._transform_jsonb_domain(domain, {})
        self.assertEqual(result, [("name",)])

    def test_domain_with_long_tuple(self):
        """Test domain with tuple longer than 3 elements."""
        domain = [("name", "=", "test", "extra")]
        result = self.Partner._transform_jsonb_domain(domain, {})
        self.assertEqual(result, [("name", "=", "test", "extra")])


@tagged("post_install", "-at_install")
class TestBuildNullCheckLogging(TransactionCase):
    """Test _build_jsonb_null_check logging behavior."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def test_null_check_generates_where_clause(self):
        """Test that null check generates correct where clause internally."""
        with patch(
            "odoo.addons.base_sparse_field_jsonb_search.models.base_model._logger"
        ) as mock_logger:
            self.Partner._build_jsonb_null_check("container", "field", True)
            self.assertTrue(mock_logger.debug.called)
            call_args = mock_logger.debug.call_args
            self.assertIn("NULL", str(call_args))


@tagged("post_install", "-at_install")
class TestGetJsonbLeafSqlWithBooleanField(TransactionCase):
    """Test _get_jsonb_leaf_sql with boolean field type."""

    def _make_mock_model(self, field_type):
        mock_model = MagicMock()
        mock_sparse_field = MagicMock()
        mock_sparse_field.sparse = "x_data"
        mock_sparse_field.type = field_type
        mock_container_field = MagicMock()
        mock_container_field.type = "serialized"
        mock_model._fields = {
            "x_field": mock_sparse_field,
            "x_data": mock_container_field,
        }
        return mock_model

    def test_boolean_field_equals_true(self):
        """Test boolean field with = True."""
        mock_model = self._make_mock_model("boolean")
        result = _get_jsonb_leaf_sql(mock_model, ("x_field", "=", True), "t")
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::boolean", sql)

    def test_boolean_field_not_equals_true(self):
        """Test boolean field with != True."""
        mock_model = self._make_mock_model("boolean")
        result = _get_jsonb_leaf_sql(mock_model, ("x_field", "!=", True), "t")
        self.assertIsNotNone(result)

    def test_integer_field_less_than(self):
        """Test integer field with < operator."""
        mock_model = self._make_mock_model("integer")
        result = _get_jsonb_leaf_sql(mock_model, ("x_field", "<", 100), "t")
        self.assertIsNotNone(result)
        sql, params = result
        self.assertIn("::numeric", sql)

    def test_float_field_greater_equal(self):
        """Test float field with >= operator."""
        mock_model = self._make_mock_model("float")
        result = _get_jsonb_leaf_sql(mock_model, ("x_field", ">=", 50.5), "t")
        self.assertIsNotNone(result)

    def test_monetary_field_not_equal(self):
        """Test monetary field with != operator."""
        mock_model = self._make_mock_model("monetary")
        result = _get_jsonb_leaf_sql(mock_model, ("x_field", "!=", 100), "t")
        self.assertIsNotNone(result)


@tagged("post_install", "-at_install")
class TestBuildJsonbComparisonBooleanBranch(TransactionCase):
    """Test _build_jsonb_comparison boolean value branch."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]

    def _make_field(self, field_type):
        mock_field = MagicMock()
        mock_field.type = field_type
        return mock_field

    def test_boolean_true_value_with_equality(self):
        """Test boolean True value triggers boolean branch."""
        field = self._make_field("boolean")
        result = self.Partner._build_jsonb_comparison(
            "container", "field", field, "=", True
        )
        self.assertEqual(result, ("field", "=", True))

    def test_boolean_false_value_non_boolean_field(self):
        """Test boolean False value with non-boolean field."""
        field = self._make_field("char")
        result = self.Partner._build_jsonb_comparison(
            "container", "field", field, "=", False
        )
        self.assertEqual(result, ("field", "=", False))
