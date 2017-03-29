# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import Iterable
from psycopg2.extensions import AsIs
# pylint: disable=W0402
from openerp.osv.expression import ExtendedLeaf, OR_OPERATOR, AND_OPERATOR,\
    FALSE_DOMAIN
from openerp import api, models
from openerp.osv import expression as expression_module
from ..expression import BaseDomainOperatorExtendedLeaf, Expression,\
    is_leaf_base_domain_operator


class BaseDomainOperator(models.AbstractModel):
    _name = 'base.domain.operator'
    _description = 'Implement custom domain operators'

    def _register_hook(self, cr):
        if not isinstance(expression_module.expression, Expression):
            expression_module.expression = Expression
            expression_module.ExtendedLeaf = BaseDomainOperatorExtendedLeaf
            expression_module.is_leaf = is_leaf_base_domain_operator

        return super(BaseDomainOperator, self)

    @api.model
    def _operator_parent_of(self, leaf, expression):
        """Implement parent_of"""

        # this function is more of less a verbatim copy of
        # https://github.com/OCA/OCB/blob/10.0/odoo/osv/expression.py#L738
        def parent_of_domain(left, ids, left_model, parent=None, prefix=''):
            if left_model._parent_store and (not left_model.pool._init) and (
                    not self.env.context.get('defer_parent_store_computation')
            ):
                doms = []
                for rec in left_model.browse(ids):
                    if doms:
                        doms.insert(0, OR_OPERATOR)
                    doms += [
                        AND_OPERATOR,
                        ('parent_right', '>', rec.parent_left),
                        ('parent_left', '<=',  rec.parent_left)
                    ]
                if prefix:
                    return [(left, 'in', left_model.search(doms).ids)]
                return doms
            else:
                parent_name = parent or left_model._parent_name
                parent_ids = set()
                for record in left_model.browse(ids):
                    while record:
                        parent_ids.add(record.id)
                        record = record[parent_name]
                return [(left, 'in', list(parent_ids))]

        fields = leaf[0].split('.')
        model = self.env[expression.root_model._name]
        field = model._fields[fields[0]]
        prefix = ''
        left = fields[0]

        if len(fields) > 1 or (
                field.type not in ('many2one', 'many2many', 'one2many') and
                field.name != 'id'
        ):
            raise NotImplementedError(
                'Only fields without dotted paths are implemented '
                'currently'
            )

        if expression.root_model._name != field.comodel_name and\
           field.comodel_name:
            model = self.env[field.comodel_name]
            prefix = field.comodel_name

        right = leaf[2]
        if not isinstance(right, Iterable):
            right = [right]

        return [
            ExtendedLeaf(p, expression.root_model)
            for p in parent_of_domain(left, right, model, prefix=prefix)
        ] or FALSE_DOMAIN

    @api.model
    def _operator_substring_of(self, leaf, expression):
        """Implement ('field', 'substring_of', 'long_string') which is `like`
        transposed"""
        field = leaf[0].split('.')[-1]
        model = expression.root_model
        return [
            ExtendedLeaf(
                (
                    'id', 'inselect',
                    (
                        'select id from "%s" where %s like %s || "%s" || %s',
                        (
                            AsIs(model._table), leaf[2], '%', AsIs(field), '%'
                        )
                    ),
                ),
                model, internal=True,
            )
        ]
