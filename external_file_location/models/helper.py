# coding: utf-8
# Author: Joel Grand-Guillaume
# Copyright 2011-2012 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)
    Generator over all subclasses of a given class, in depth first order.
    >>> list(itersubclasses(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>>
    >>> for cls in itersubclasses(A):
    ... print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls
                        )
    if _seen is None:
        _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError:  # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


def _get_erp_module_name(module_path):
    # see this PR for v9 https://github.com/odoo/odoo/pull/11084
    """ Extract the name of the Odoo module from the path of the
    Python module.

    Taken from Odoo server: ``openerp.models.MetaModel``

    The (Odoo) module name can be in the ``openerp.addons`` namespace
    or not. For instance module ``sale`` can be imported as
    ``openerp.addons.sale`` (the good way) or ``sale`` (for backward
    compatibility).
    """
    module_parts = module_path.split('.')
    if len(module_parts) > 2 and module_parts[:2] == ['openerp', 'addons']:
        module_name = module_parts[2]
    else:
        module_name = module_parts[0]
    return module_name


def is_module_installed(env, module_name):
    """ Check if an Odoo addon is installed.

    :param module_name: name of the addon
    """
    # the registry maintains a set of fully loaded modules so we can
    # lookup for our module there
    return module_name in env.registry._init_modules


def get_erp_module(cls_or_func):
    """ For a top level function or class, returns the
    name of the Odoo module where it lives.

    So we will be able to filter them according to the modules
    installation state.
    """
    return _get_erp_module_name(cls_or_func.__module__)
