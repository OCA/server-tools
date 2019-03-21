# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api
# pylint: disable=W0402
from odoo.osv.expression import ExtendedLeaf, expression, is_operator,\
    is_leaf


class BaseDomainOperatorExtendedLeaf(ExtendedLeaf):
    def __init__(self, leaf, model, join_context=None, internal=False):
        if isinstance(leaf, ExtendedLeaf):
            # TODO: think very long and hard if this introduces a security
            # problem
            internal = True
            model = leaf.model
            join_context = (join_context or []) + leaf.join_context
            leaf = leaf.leaf
        super(BaseDomainOperatorExtendedLeaf, self).__init__(
            leaf, model, join_context=join_context, internal=internal
        )


class Expression(expression):

    def parse(self):
        domain = []
        env = self.root_model.env
        if 'base.domain.operator' not in env.registry:
            # this can happen during intialization
            return super(Expression, self).parse()
        base_domain_operator = env['base.domain.operator']
        for leaf in self.expression:
            if not is_operator(leaf):
                handler = '_operator_%s' % leaf[1].replace(' ', '_')
                if hasattr(base_domain_operator, handler):
                    domain.extend(
                        getattr(base_domain_operator, handler)(
                            leaf, self
                        )
                    )
                else:
                    domain.append(leaf)
            else:
                domain.append(leaf)
        self.expression = domain
        return super(Expression, self).parse()


def is_leaf_base_domain_operator(element, internal=False):
    result = is_leaf(element, internal=internal)
    if not result and (
            isinstance(element, tuple) or isinstance(element, list)
    ) and len(element) > 1:
        # see if we have an environment with this operator
        for env in api.Environment.envs:
            if 'base.domain.operator' in env.registry:
                result = hasattr(
                    env['base.domain.operator'],
                    '_operator_%s' % element[1].replace(' ', '_')
                )
            break
    return result
