import re
import readline
import rlcompleter

# Common models.Model methods surfaced in completion alongside field names
_MODEL_METHODS = (
    "browse",
    "create",
    "copy",
    "unlink",
    "read",
    "write",
    "search",
    "search_count",
    "search_fetch",
    "read_group",
    "filtered",
    "filtered_domain",
    "mapped",
    "sorted",
    "ensure_one",
    "exists",
    "name_search",
    "name_get",
    "default_get",
    "fields_get",
    "sudo",
    "with_context",
    "with_user",
    "with_company",
)


def _complete_dotted_field(env, model_name, field_prefix):
    """Complete dotted field paths like 'partner_id.name_', navigating relations."""
    parts = field_prefix.split(".")
    current_model = model_name

    # Navigate through all parts except the last (traverse relation chain)
    for part in parts[:-1]:
        if current_model not in env.registry.models:
            return []
        field = env.registry.models[current_model]._fields.get(part)
        comodel = getattr(field, "comodel_name", None) if field else None
        if not comodel:
            return []
        current_model = comodel

    if current_model not in env.registry.models:
        return []

    last_prefix = parts[-1]
    path_prefix = ".".join(parts[:-1])
    if path_prefix:
        path_prefix += "."

    return [
        path_prefix + f
        for f in env.registry.models[current_model]._fields
        if f.startswith(last_prefix)
    ]


def _field_and_method_matches(env, model_name, prefix):
    """Return '.<name>' completions for fields then common methods, deduplicated."""
    fields = [f for f in env[model_name]._fields if f.startswith(prefix)]
    methods = [
        m
        for m in _MODEL_METHODS
        if m.startswith(prefix) and m not in env[model_name]._fields
    ]
    return ["." + n for n in fields + methods]


def _setup():
    try:
        from odoo.cli.shell import Console
    except ImportError:
        return

    _original_init = Console.__init__

    def _patched_init(self, locals=None, filename="<console>"):  # pylint: disable=redefined-builtin
        _original_init(self, locals, filename)

        shell_locals = locals or {}
        python_completer = rlcompleter.Completer(shell_locals).complete

        def smart_completer(text, state):
            line = readline.get_line_buffer()
            env = shell_locals.get("env")

            if env is not None:
                # Field on browse/search result: env['sale.order'].browse(1).name_
                #                                env['sale.order'].search([...]).name_
                # ')' is a readline delimiter so text includes the leading '.'.
                # Greedy '.*' finds the outermost closing ')' even when the args
                # contain nested parens (e.g. domain tuples).
                result_match = re.search(
                    r"env\[(['\"])([^'\"]+)\1\]\.\w+\(.*\)\.([\w]*)$", line
                )
                if result_match:
                    model_name = result_match.group(2)
                    field_prefix = result_match.group(3)
                    if model_name in env.registry.models:
                        matches = _field_and_method_matches(
                            env, model_name, field_prefix
                        )
                        try:
                            return matches[state]
                        except IndexError:
                            return None

                # Field/method access: env['sale.order'].sea → .search, .search_count
                # ']' is a readline delimiter so text includes the leading '.'.
                field_match = re.search(r"env\[(['\"])([^'\"]+)\1\]\.([\w]*)$", line)
                if field_match:
                    model_name = field_match.group(2)
                    field_prefix = field_match.group(3)
                    if model_name in env.registry.models:
                        matches = _field_and_method_matches(
                            env, model_name, field_prefix
                        )
                        try:
                            return matches[state]
                        except IndexError:
                            return None

                # Field name inside method args: env['sale.order'].search([('name_
                # Also handles dotted paths: env['sale.order'].mapped('partner_id.name_
                # '(' and "'" are readline delimiters so text = the partial field name
                method_match = re.search(
                    r"env\[(['\"])([^'\"]+)\1\]\..*\(\s*['\"]([^'\"]*)$", line
                )
                if method_match:
                    model_name = method_match.group(2)
                    matches = _complete_dotted_field(env, model_name, text)
                    try:
                        return matches[state]
                    except IndexError:
                        return None

                # Model name completion: env['sale.
                if re.search(r"env\[['\"][\w.]*$", line):
                    matches = [m for m in env.registry.models if m.startswith(text)]
                    try:
                        return matches[state]
                    except IndexError:
                        return None

            return python_completer(text, state)

        readline.set_completer(smart_completer)
        readline.parse_and_bind("tab: complete")

    Console.__init__ = _patched_init


_setup()
