# Copyright 2026 OCA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from odoo.tests import common

from odoo.addons.shell_model_autocomplete.dev_tools.shell_auto_completer import (
    _MODEL_METHODS,
    _complete_dotted_field,
    _field_and_method_matches,
    _setup,
)


def _make_env(models_fields):
    """Build a lightweight mock env for the given {model: [field, ...]} mapping.

    Each model gets a mock that exposes:
    - env.registry.models[model_name]._fields  – a dict keyed by field name
    - env[model_name]._fields                  – same dict
    Relational fields carry a ``comodel_name`` attribute when listed as
    ``(field_name, comodel)`` 2-tuples instead of plain strings.
    """
    registry_models = {}
    env_items = {}

    for model_name, field_specs in models_fields.items():
        fields_dict = {}
        for spec in field_specs:
            if isinstance(spec, tuple):
                fname, comodel = spec
                f = MagicMock()
                f.comodel_name = comodel
            else:
                fname = spec
                f = MagicMock(spec=[])  # no comodel_name attribute
            fields_dict[fname] = f

        model_mock = MagicMock()
        model_mock._fields = fields_dict
        registry_models[model_name] = model_mock
        env_items[model_name] = model_mock

    registry = MagicMock()
    registry.models = registry_models

    env = MagicMock()
    env.registry = registry
    env.__getitem__ = lambda self_, key: env_items[key]
    return env


class TestCompleteDottedField(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.env_mock = _make_env(
            {
                "sale.order": [
                    "name",
                    "state",
                    ("partner_id", "res.partner"),
                ],
                "res.partner": [
                    "name",
                    "email",
                    ("company_id", "res.company"),
                ],
                "res.company": ["name", "currency_id"],
            }
        )

    def test_simple_prefix(self):
        """Top-level field prefix returns matching field names."""
        matches = _complete_dotted_field(self.env_mock, "sale.order", "na")
        self.assertIn("name", matches)
        self.assertNotIn("state", matches)

    def test_simple_all_fields(self):
        """Empty prefix returns all fields."""
        matches = _complete_dotted_field(self.env_mock, "sale.order", "")
        self.assertIn("name", matches)
        self.assertIn("state", matches)
        self.assertIn("partner_id", matches)

    def test_dotted_one_level(self):
        """One-level dotted path navigates through relation."""
        matches = _complete_dotted_field(self.env_mock, "sale.order", "partner_id.na")
        self.assertIn("partner_id.name", matches)
        self.assertNotIn("partner_id.email", matches)

    def test_dotted_two_levels(self):
        """Two-level dotted path navigates two relations."""
        matches = _complete_dotted_field(
            self.env_mock, "sale.order", "partner_id.company_id.na"
        )
        self.assertIn("partner_id.company_id.name", matches)

    def test_unknown_root_model(self):
        """Unknown root model returns empty list."""
        matches = _complete_dotted_field(self.env_mock, "unknown.model", "name")
        self.assertEqual(matches, [])

    def test_unknown_intermediate_model(self):
        """Navigating to a comodel that is not in the registry returns empty list."""
        env = _make_env(
            {
                "sale.order": [("partner_id", "nonexistent.model")],
            }
        )
        matches = _complete_dotted_field(env, "sale.order", "partner_id.name")
        self.assertEqual(matches, [])

    def test_field_without_comodel(self):
        """Non-relational field in the middle of a dotted path returns empty list."""
        matches = _complete_dotted_field(self.env_mock, "sale.order", "name.something")
        self.assertEqual(matches, [])

    def test_nonexistent_intermediate_field(self):
        """Missing intermediate field returns empty list."""
        matches = _complete_dotted_field(
            self.env_mock, "sale.order", "nonexistent_field.name"
        )
        self.assertEqual(matches, [])


class TestFieldAndMethodMatches(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.env_mock = _make_env(
            {
                "sale.order": [
                    "name",
                    "state",
                    "note",
                    "search_custom",  # overlaps with method prefix
                ]
            }
        )

    def test_field_completions_have_dot_prefix(self):
        """All returned completions start with a leading dot."""
        matches = _field_and_method_matches(self.env_mock, "sale.order", "na")
        self.assertTrue(all(m.startswith(".") for m in matches))

    def test_field_prefix_filters(self):
        matches = _field_and_method_matches(self.env_mock, "sale.order", "na")
        self.assertIn(".name", matches)
        self.assertNotIn(".state", matches)

    def test_method_completions_included(self):
        """Methods from _MODEL_METHODS appear when they match the prefix."""
        matches = _field_and_method_matches(self.env_mock, "sale.order", "brow")
        self.assertIn(".browse", matches)

    def test_method_not_duplicated_when_also_a_field(self):
        """A method that is also a field name must not be returned twice."""
        # 'search_custom' starts with 'search' – the 'search' method should
        # appear once, not duplicated.
        matches = _field_and_method_matches(self.env_mock, "sale.order", "search")
        dot_search = [m for m in matches if m == ".search"]
        self.assertEqual(len(dot_search), 1)

    def test_empty_prefix_returns_all(self):
        matches = _field_and_method_matches(self.env_mock, "sale.order", "")
        for method in _MODEL_METHODS:
            self.assertIn("." + method, matches)
        self.assertIn(".name", matches)

    def test_no_match_returns_empty(self):
        matches = _field_and_method_matches(self.env_mock, "sale.order", "zzz")
        self.assertEqual(matches, [])


class TestSetupImportError(common.TransactionCase):
    def test_setup_handles_import_error_gracefully(self):
        """_setup must not raise when odoo.cli.shell is unavailable."""
        with patch.dict("sys.modules", {"odoo.cli.shell": None}):
            try:
                _setup()
            except Exception as exc:  # pragma: no cover
                self.fail(f"_setup raised unexpectedly: {exc}")


class TestSmartCompleter(common.TransactionCase):
    """Test the smart_completer closure created inside _patched_init."""

    @contextmanager
    def _patched_completer(self, env_mock=None):
        """Context manager that sets up mocks, runs _setup(), triggers
        _patched_init, and yields (completer_fn, mock_readline) while the
        readline patch remains active so that smart_completer can call
        readline.get_line_buffer() on the mock.

        Uses a real Python class for Console so that _setup() can assign to
        ``Console.__init__`` without hitting MagicMock magic-method restrictions.
        """
        captured = {}

        mock_readline = MagicMock()
        mock_readline.get_line_buffer.return_value = ""

        def fake_set_completer(fn):
            captured["completer"] = fn

        mock_readline.set_completer.side_effect = fake_set_completer

        class FakeConsole:
            def __init__(self, locals=None, filename="<console>"):
                pass

        fake_shell_mod = MagicMock()
        fake_shell_mod.Console = FakeConsole

        with (
            patch(
                "odoo.addons.shell_model_autocomplete.dev_tools."
                "shell_auto_completer.readline",
                mock_readline,
            ),
            patch.dict("sys.modules", {"odoo.cli.shell": fake_shell_mod}),
        ):
            _setup()
            # Trigger _patched_init (which _setup just installed) so that
            # smart_completer gets created and registered via set_completer.
            shell_locals = {"env": env_mock} if env_mock else {}
            instance = object.__new__(FakeConsole)
            FakeConsole.__init__(instance, locals=shell_locals, filename="<console>")
            # Yield while patches are still active so smart_completer can
            # access mock_readline.get_line_buffer().
            yield captured["completer"], mock_readline

    def _make_full_env(self):
        return _make_env(
            {
                "sale.order": [
                    "name",
                    "state",
                    ("partner_id", "res.partner"),
                ],
                "res.partner": ["name", "email"],
            }
        )

    # ------------------------------------------------------------------
    # Model-name completion: env['sale.
    # ------------------------------------------------------------------
    def test_model_name_completion(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = "env['sale."
            self.assertEqual(completer("sale.", 0), "sale.order")

    def test_model_name_completion_state_1_returns_none_when_single_match(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = "env['sale."
            self.assertEqual(completer("sale.", 0), "sale.order")
            self.assertIsNone(completer("sale.", 1))

    def test_model_name_no_match(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = "env['zzz."
            self.assertIsNone(completer("zzz.", 0))

    # ------------------------------------------------------------------
    # Field/method access: env['sale.order'].sea
    # ------------------------------------------------------------------
    def test_field_access_completion(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = "env['sale.order'].na"
            self.assertEqual(completer(".na", 0), ".name")

    def test_field_access_method_completion(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = "env['sale.order'].brow"
            self.assertEqual(completer(".brow", 0), ".browse")

    def test_field_access_unknown_model_falls_through(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = "env['unknown.model'].na"
            # Model not in registry → falls through to python_completer
            # rlcompleter returns None for ".na" in an empty namespace
            self.assertIsNone(completer(".na", 0))

    def test_field_access_out_of_range_state(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = "env['sale.order'].zzz"
            self.assertIsNone(completer(".zzz", 0))

    # ------------------------------------------------------------------
    # Result field access: env['sale.order'].browse(1).na
    # ------------------------------------------------------------------
    def test_result_field_completion(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = (
                "env['sale.order'].browse(1).na"
            )
            self.assertEqual(completer(".na", 0), ".name")

    def test_result_field_completion_nested_parens(self):
        """Greedy .* handles nested parentheses in method args."""
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = (
                "env['sale.order'].search([('state', '=', 'sale')]).na"
            )
            self.assertEqual(completer(".na", 0), ".name")

    def test_result_field_out_of_range_state(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = (
                "env['sale.order'].browse(1).na"
            )
            self.assertEqual(completer(".na", 0), ".name")
            self.assertIsNone(completer(".na", 100))

    def test_result_field_unknown_model(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = (
                "env['unknown.model'].browse(1).na"
            )
            self.assertIsNone(completer(".na", 0))

    # ------------------------------------------------------------------
    # Field name inside method args: env['sale.order'].search([('name_
    # ------------------------------------------------------------------
    def test_method_arg_field_completion(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = (
                "env['sale.order'].search([('na"
            )
            self.assertEqual(completer("na", 0), "name")

    def test_method_arg_dotted_field_completion(self):
        """Dotted path inside method args navigates the relation."""
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = (
                "env['sale.order'].mapped('partner_id.na"
            )
            self.assertEqual(completer("partner_id.na", 0), "partner_id.name")

    def test_method_arg_no_match(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = (
                "env['sale.order'].search([('zzz"
            )
            self.assertIsNone(completer("zzz", 0))

    def test_method_arg_out_of_range_state(self):
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = (
                "env['sale.order'].search([('na"
            )
            self.assertEqual(completer("na", 0), "name")
            self.assertIsNone(completer("na", 100))

    # ------------------------------------------------------------------
    # Fallback to Python completer
    # ------------------------------------------------------------------
    def test_fallback_python_completer_no_env(self):
        """Without env the smart_completer falls back to rlcompleter."""
        with self._patched_completer(env_mock=None) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = "some_python_expr"
            # rlcompleter returns None for unknown names in an empty namespace
            self.assertIsNone(completer("some", 0))

    def test_fallback_python_completer_non_env_line(self):
        """Lines that don't match any env pattern fall back to rlcompleter."""
        env = self._make_full_env()
        with self._patched_completer(env) as (completer, mock_readline):
            mock_readline.get_line_buffer.return_value = "print('hello')"
            # rlcompleter recognises 'print' as a builtin
            self.assertEqual(completer("pri", 0), "print(")
