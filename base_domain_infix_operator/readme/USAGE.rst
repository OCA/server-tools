>>> from odoo.addons.base_domain_infix_operator.infix_expression import to_infix_domain
>>>
>>> prefix_domain = ["!", "&", ("a", "=", "b"), "!", ("c", "=", "d"), "|", ("e", "=", "f"), "!", ("g", "=", "h")]
>>> to_infix_domain(prefix_domain)
[(('NOT', (('a', '=', 'b'), 'AND', ('NOT', ('c', '=', 'd')))), 'AND', (('e', '=', 'f'), 'OR', ('NOT', ('g', '=', 'h'))))]
