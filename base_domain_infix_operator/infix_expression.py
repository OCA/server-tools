#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from inspect import signature

from odoo.osv.expression import (
    AND_OPERATOR as PREFIX_AND_OPERATOR,
    NOT_OPERATOR as PREFIX_NOT_OPERATOR,
    OR_OPERATOR as PREFIX_OR_OPERATOR,
    normalize_domain,
)

NOT_OPERATOR = "NOT"
AND_OPERATOR = "AND"
OR_OPERATOR = "OR"


def _not_term(term):
    return NOT_OPERATOR, term


def _and_term(first, second):
    return first, AND_OPERATOR, second


def _or_term(first, second):
    return first, OR_OPERATOR, second


PREFIX_OP_TO_INFIX_TERM_FUNC = {
    PREFIX_NOT_OPERATOR: lambda l: _not_term(l),
    PREFIX_AND_OPERATOR: lambda l1, l2: _and_term(l1, l2),
    PREFIX_OR_OPERATOR: lambda l1, l2: _or_term(l1, l2),
}


def to_infix_domain(prefix_domain):
    """
    Convert a domain from prefix operator to infix operator.
    >>> to_infix_domain(["&", ("a", "=", "b"), ("c", "=", "d")])
    [(("a", "=", "b"), "AND", ("c", "=", "d"))]
    """
    prefix_domain = normalize_domain(prefix_domain)

    infix_domain = []
    for term in reversed(prefix_domain):
        infix_term_func = PREFIX_OP_TO_INFIX_TERM_FUNC.get(term)
        if infix_term_func is not None:
            parameters = [
                infix_domain.pop() for _p in signature(infix_term_func).parameters
            ]
            infix_term = infix_term_func(*parameters)
        else:
            infix_term = term
        infix_domain.append(infix_term)
    return infix_domain
