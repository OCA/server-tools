# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.osv.expression import (
    AND,
    AND_OPERATOR,
    DOMAIN_OPERATORS,
    NOT_OPERATOR,
    OR,
    OR_OPERATOR,
)


def inverse_combine(domain, operator):
    """Decompose normalized domain into operands according to operator

    The result can be then altered easily to inject domain operands before
    rebuilding a new domain using the corresponding function from osv.expression.

    :param domain: A normalized domain
    :param operator: The "main" domain operator of the domain being either '&' or '|'
                     (must be the first operator in a normalized domain)

    :return list: A list of domains
    """
    if operator not in DOMAIN_OPERATORS:
        raise Exception("Unsupported operator parameter: %s" % operator)
    operator_func = {AND_OPERATOR: AND, OR_OPERATOR: OR}
    other_operator = OR_OPERATOR if operator == AND_OPERATOR else AND_OPERATOR
    result = []
    operator_elements_stack = []
    other_elements_stack = []
    elements_stack = []

    last_element = False

    # 1. Loop over the domain in reverse order
    for element in reversed(domain):
        if element == NOT_OPERATOR:
            raise Exception(
                "Inversing domains including NOT operator ('!') is not supported"
            )
        if element in DOMAIN_OPERATORS:
            # 3. When we reach an operator:
            # - pop the last item from the element stack to the corresponding operator stack
            # - if such stack contains only one element, the actual operator applies to the two
            #   last items in the elements stack, so pop the penultimate item as well
            if element != operator:
                if len(elements_stack) > 0:
                    other_elements_stack.append([elements_stack.pop()])
                    if (
                        len(other_elements_stack) == 1
                        and last_element not in DOMAIN_OPERATORS
                    ):
                        other_elements_stack.append([elements_stack.pop()])
            else:
                if len(elements_stack) > 0:
                    operator_elements_stack.append([elements_stack.pop()])
                    if (
                        len(operator_elements_stack) == 1
                        and last_element not in DOMAIN_OPERATORS
                    ):
                        operator_elements_stack.append([elements_stack.pop()])
            last_element = element
        else:
            # 4. If actual element is a tuple, but last element was an operator, empty the
            # corresponding operator stack into the result
            if last_element in DOMAIN_OPERATORS:
                if last_element != operator:
                    result.append(operator_func[last_element](other_elements_stack))
                    other_elements_stack = []
                else:
                    # TODO: Add tests to cover these lines (and eventually fix these)
                    result.append(operator_func[last_element](operator_elements_stack))
                    operator_elements_stack = []
            # 2. Add any tuple element to the stack
            elements_stack.append(element)
            last_element = element
    # 5. Empty operators stack when reaching the end
    if operator_elements_stack:
        operator_elements_stack.extend(result)
        result = operator_elements_stack
    elif other_elements_stack:
        result.append(operator_func[other_operator](other_elements_stack))
    return result


def inverse_OR(domain):
    return inverse_combine(domain, OR_OPERATOR)


def inverse_AND(domain):
    return inverse_combine(domain, AND_OPERATOR)
