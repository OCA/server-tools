# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
"""Minimal ``Domain`` shim backporting the Odoo 19+ ``odoo.fields.Domain`` API.

Odoo 19 replaced list-domains by a ``Domain`` AST object (``odoo/orm/domains.py``,
~2000 lines). Backported modules written against 19/20 import it as
``from odoo.fields import Domain``. Rather than porting the whole engine, this
shim reimplements *only* the surface those modules use, delegating to 18's
``odoo.osv.expression``.

Because ``Domain`` subclasses ``list`` and normalises itself to a plain 18
list-domain, a shim instance can be passed straight to ``search``/``_search``.

Supported surface (extend as new call sites appear):
- ``Domain([('a', '=', 1), ...])`` and ``Domain('a', '=', 1)`` constructors
- ``&`` / ``|`` / ``~`` operators
- ``Domain.AND(iterable)`` / ``Domain.OR(iterable)``
- ``Domain.TRUE`` / ``Domain.FALSE``
- ``.optimize_full(model)`` -> validates against the model, returns self

NOT supported (keep such call sites hand-adapted on 18):
- relative-date literals in leaves (e.g. ``('date', '<', '-1d')``)
- custom SQL domains, ``any!``/``not any!`` internal operators
"""

from odoo.osv import expression


class Domain(list):
    def __init__(self, *args):
        if len(args) == 3:
            domain = [tuple(args)]
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, Domain):
                domain = list(arg)
            elif arg is True or arg == []:
                domain = list(expression.TRUE_DOMAIN)
            elif arg is False:
                domain = list(expression.FALSE_DOMAIN)
            elif isinstance(arg, list | tuple):
                domain = expression.normalize_domain(list(arg))
            else:
                raise TypeError(f"Domain() invalid argument type: {arg!r}")
        else:
            raise TypeError(f"Domain() invalid arguments: {args!r}")
        super().__init__(domain)

    def __and__(self, other):
        return Domain(expression.AND([list(self), list(Domain(other))]))

    __rand__ = __and__

    def __or__(self, other):
        return Domain(expression.OR([list(self), list(Domain(other))]))

    __ror__ = __or__

    def __invert__(self):
        return Domain(["!"] + list(self))

    @staticmethod
    def AND(items):
        return Domain(expression.AND([list(Domain(item)) for item in items]))

    @staticmethod
    def OR(items):
        return Domain(expression.OR([list(Domain(item)) for item in items]))

    def optimize_full(self, model):
        """Validate the domain against ``model`` (raises on unknown fields)."""
        model._where_calc(list(self))
        return self


# v19/v20 call sites reference ``Domain.TRUE`` / ``Domain.FALSE`` as attributes.
Domain.TRUE = Domain(True)
Domain.FALSE = Domain(False)
