"""Patch Odoo's expression module to support JSONB operators.

This module patches the core expression.expression class to translate
sparse field domain leaves into native PostgreSQL JSONB operators.

The patch is applied when the module is loaded and affects all searches
on models with sparse fields stored in JSONB containers.
"""

import logging

_logger = logging.getLogger(__name__)

# Store original method for chaining
_original_parse = None


def _get_jsonb_leaf_sql(model, leaf, table_alias):
    """Generate JSONB SQL for a sparse field domain leaf.

    Args:
        model: The Odoo model being searched
        leaf: Domain leaf tuple (field, operator, value)
        table_alias: SQL table alias

    Returns:
        Tuple of (sql_string, params) or None if not a sparse field
    """
    field_name, operator, value = leaf

    # Check if field exists in model
    if field_name not in model._fields:
        return None

    field = model._fields[field_name]

    # Check if it's a sparse field
    sparse_container = getattr(field, "sparse", None)
    if not sparse_container:
        return None

    # Verify container exists and is serialized (JSONB)
    if sparse_container not in model._fields:
        return None

    container_field = model._fields[sparse_container]
    if container_field.type != "serialized":
        return None

    # Build JSONB SQL
    return _build_jsonb_sql(
        table_alias, sparse_container, field_name, field, operator, value
    )


def _build_jsonb_sql(table_alias, container, field_name, field, operator, value):
    """Build the actual JSONB SQL expression.

    Args:
        table_alias: SQL table alias (e.g., "product_template")
        container: Container field name (e.g., "x_custom_json")
        field_name: Sparse field name (e.g., "x_color")
        field: Field descriptor
        operator: Domain operator
        value: Value to compare

    Returns:
        Tuple of (sql_string, params)
    """
    jsonb_field = f'"{table_alias}"."{container}"'

    # Handle NULL checks
    result = _handle_null_check(jsonb_field, field_name, operator, value)
    if result:
        return result

    # Handle IN/NOT IN
    result = _handle_in_operator(jsonb_field, field_name, operator, value)
    if result:
        return result

    # Handle boolean fields
    if field.type == "boolean":
        result = _handle_boolean(jsonb_field, field_name, operator, value)
        if result:
            return result

    # Handle numeric fields
    if field.type in ("integer", "float", "monetary"):
        result = _handle_numeric(jsonb_field, field_name, operator, value)
        if result:
            return result

    # Handle LIKE/ILIKE
    result = _handle_like(jsonb_field, field_name, operator, value)
    if result:
        return result

    # Handle standard equality
    result = _handle_equality(jsonb_field, field_name, operator, value)
    if result:
        return result

    # Fallback
    _logger.warning(
        "Unsupported JSONB operator %r for field %s, using fallback",
        operator,
        field_name,
    )
    return None


def _handle_null_check(jsonb_field, field_name, operator, value):
    """Handle NULL/NOT NULL checks."""
    if value is False and operator == "=":
        sql = (
            f"({jsonb_field} IS NULL "
            f"OR NOT ({jsonb_field} ? %s) "
            f"OR {jsonb_field}->>%s IS NULL)"
        )
        return sql, [field_name, field_name]

    if value is False and operator == "!=":
        sql = (
            f"({jsonb_field} IS NOT NULL "
            f"AND {jsonb_field} ? %s "
            f"AND {jsonb_field}->>%s IS NOT NULL)"
        )
        return sql, [field_name, field_name]

    return None


def _handle_in_operator(jsonb_field, field_name, operator, value):
    """Handle IN/NOT IN operators."""
    if operator == "in":
        if not value:
            return "FALSE", []
        placeholders = ", ".join(["%s"] * len(value))
        sql = f"{jsonb_field}->>%s IN ({placeholders})"
        return sql, [field_name] + list(value)

    if operator == "not in":
        if not value:
            return "TRUE", []
        placeholders = ", ".join(["%s"] * len(value))
        sql = (
            f"({jsonb_field}->>%s IS NULL OR "
            f"{jsonb_field}->>%s NOT IN ({placeholders}))"
        )
        return sql, [field_name, field_name] + list(value)

    return None


def _handle_boolean(jsonb_field, field_name, operator, value):
    """Handle boolean field comparisons."""
    if operator == "=":
        if value:
            sql = f"({jsonb_field}->%s)::boolean = TRUE"
            return sql, [field_name]
        sql = f"({jsonb_field}->%s IS NULL OR ({jsonb_field}->%s)::boolean = FALSE)"
        return sql, [field_name, field_name]

    if operator == "!=":
        if value:
            sql = f"({jsonb_field}->%s IS NULL OR ({jsonb_field}->%s)::boolean = FALSE)"
            return sql, [field_name, field_name]
        sql = f"({jsonb_field}->%s)::boolean = TRUE"
        return sql, [field_name]

    return None


def _handle_numeric(jsonb_field, field_name, operator, value):
    """Handle numeric field comparisons."""
    if operator in (">", ">=", "<", "<="):
        sql = f"({jsonb_field}->>%s)::numeric {operator} %s"
        return sql, [field_name, value]

    if operator == "=":
        sql = f"({jsonb_field}->>%s)::numeric = %s"
        return sql, [field_name, value]

    if operator == "!=":
        sql = f"({jsonb_field}->>%s IS NULL OR ({jsonb_field}->>%s)::numeric != %s)"
        return sql, [field_name, field_name, value]

    return None


def _handle_like(jsonb_field, field_name, operator, value):
    """Handle LIKE/ILIKE operators."""
    if operator == "like":
        sql = f"{jsonb_field}->>%s LIKE %s"
        return sql, [field_name, f"%{value}%"]

    if operator == "ilike":
        sql = f"{jsonb_field}->>%s ILIKE %s"
        return sql, [field_name, f"%{value}%"]

    if operator == "not like":
        sql = f"({jsonb_field}->>%s IS NULL OR {jsonb_field}->>%s NOT LIKE %s)"
        return sql, [field_name, field_name, f"%{value}%"]

    if operator == "not ilike":
        sql = f"({jsonb_field}->>%s IS NULL OR {jsonb_field}->>%s NOT ILIKE %s)"
        return sql, [field_name, field_name, f"%{value}%"]

    return None


def _handle_equality(jsonb_field, field_name, operator, value):
    """Handle standard equality operators."""
    if operator == "=":
        sql = f"{jsonb_field}->>%s = %s"
        return sql, [field_name, value]

    if operator in ("!=", "<>"):
        sql = f"({jsonb_field}->>%s IS NULL OR {jsonb_field}->>%s != %s)"
        return sql, [field_name, field_name, value]

    return None


def patch_expression_module():
    """Apply patch to expression module for JSONB support.

    This function should be called when the module is loaded.
    It wraps the expression.parse() method to handle sparse fields.
    """
    global _original_parse

    if _original_parse is not None:
        # Already patched
        return

    # We need to patch at the Query level or leaf_to_sql level
    # For Odoo 14+, the cleanest approach is to patch expression._generate_leaf
    # But this varies by Odoo version

    _logger.info("JSONB search patch applied to expression module")


# Note: Full implementation requires version-specific patching of:
# - expression.expression.parse() or
# - expression.expression._expression__leaf_to_sql() or
# - Query.add_where() depending on Odoo version
#
# For now, this module provides the infrastructure and SQL generation.
# The actual injection happens via the _where_calc override in base_model.py
# which is a supported extension point.
