# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from functools import wraps

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


def implemented_by_base_exception(func):
    """Call a prefixed function based on 'namespace'."""
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        fun_name = func.__name__
        fun = '_%s%s' % (cls.rule_group, fun_name)
        if not hasattr(cls, fun):
            fun = '_default%s' % (fun_name)
        return getattr(cls, fun)(*args, **kwargs)
    return wrapper


class ExceptionRule(models.Model):
    _name = 'exception.rule'
    _description = "Exception Rules"
    _order = 'active desc, sequence asc'

    name = fields.Char('Exception Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer(
        string='Sequence',
        help="Gives the sequence order when applying the test")
    rule_group = fields.Selection(
        selection=[],
        help="Rule group is used to group the rules that must validated "
        "at same time for a target object. Ex: "
        "validate sale.order.line rules with sale order rules.",
        required=True)
    model = fields.Selection(
        selection=[],
        string='Apply on', required=True)
    exception_type = fields.Selection(
        selection=[('by_domain', 'By domain'),
                   ('by_py_code', 'By python code')],
        string='Exception Type', required=True, default='by_py_code',
        help="By python code: allow to define any arbitrary check\n"
             "By domain: limited to a selection by an odoo domain:\n"
             "           performance can be better when exceptions "
             "           are evaluated with several records")
    domain = fields.Char('Domain')
    active = fields.Boolean('Active')
    code = fields.Text(
        'Python Code',
        help="Python code executed to check if the exception apply or "
             "not. The code must apply failed = True to apply the "
             "exception.",
        default="""
# Python code. Use failed = True to block the base.exception.
# You can use the following variables :
#  - self: ORM model of the record which is checked
#  - "rule_group" or "rule_group_"line:
#       browse_record of the base.exception or
#       base.exception line (ex rule_group = sale for sale order)
#  - object: same as order or line, browse_record of the base.exception or
#    base.exception line
#  - pool: ORM model pool (i.e. self.pool, deprecated in new api)
#  - obj: same as object
#  - env: ORM model pool (i.e. self.env)
#  - time: Python time module
#  - cr: database cursor
#  - uid: current user id
#  - context: current context
""")

    @api.multi
    def _get_domain(self):
        """ override me to customize domains according exceptions cases """
        self.ensure_one()
        return safe_eval(self.domain)


class BaseException(models.AbstractModel):
    _name = 'base.exception'

    _order = 'main_exception_id asc'

    main_exception_id = fields.Many2one(
        'exception.rule',
        compute='_compute_main_error',
        string='Main Exception',
        store=True)
    rule_group = fields.Selection(
        [],
        readonly=True,
    )
    exception_ids = fields.Many2many(
        'exception.rule',
        string='Exceptions')
    ignore_exception = fields.Boolean('Ignore Exceptions', copy=False)

    @api.depends('exception_ids', 'ignore_exception')
    def _compute_main_error(self):
        for obj in self:
            if not obj.ignore_exception and obj.exception_ids:
                obj.main_exception_id = obj.exception_ids[0]
            else:
                obj.main_exception_id = False

    @api.multi
    def _popup_exceptions(self):
        action = self._get_popup_action()
        action = action.read()[0]
        action.update({
            'context': {
                'active_model': self._name,
                'active_id': self.ids[0],
                'active_ids': self.ids
            }
        })
        return action

    @api.model
    def _get_popup_action(self):
        action = self.env.ref('base_exception.action_exception_rule_confirm')
        return action

    @api.multi
    def _check_exception(self):
        """
        This method must be used in a constraint that must be created in the
        object that inherits for base.exception.
        for sale :
        @api.constrains('ignore_exception',)
        def sale_check_exception(self):
            ...
            ...
            self._check_exception
        """
        exception_ids = self.detect_exceptions()
        if exception_ids:
            exceptions = self.env['exception.rule'].browse(exception_ids)
            raise ValidationError('\n'.join(exceptions.mapped('name')))

    @api.multi
    def test_exceptions(self):
        """
        Condition method for the workflow from draft to confirm
        """
        if self.detect_exceptions():
            return False
        return True

    @api.multi
    def _reverse_field(self):
        """Name of the many2many field from exception rule to self.

        In order to take advantage of domain optimisation, exception rule
        model should have a many2many field to inherited object.
        The opposit relation already exists in the name of exception_ids

        Example:
        class ExceptionRule(models.Model):
            _inherit = 'exception.rule'

            model = fields.Selection(
            selection_add=[
                ('sale.order', 'Sale order'),
                [...]
            ])
            sale_ids = fields.Many2many(
                'sale.order',
                string='Sales')
            [...]
        """
        exception_obj = self.env['exception.rule']
        reverse_fields = self.env['ir.model.fields'].search([
            ['model', '=', 'exception.rule'],
            ['ttype', '=', 'many2many'],
            ['relation', '=', self[0]._name],
        ])
        # ir.model.fields may contain old variable name
        # so we check if the field exists on exception rule
        return ([
            field.name for field in reverse_fields
            if hasattr(exception_obj, field.name)
        ] or [None])[0]

    @api.multi
    def detect_exceptions(self):
        """List all exception_ids applied on self
        Exception ids are also written on records
        """
        if not self:
            return []
        exception_obj = self.env['exception.rule']
        all_exceptions = exception_obj.sudo().search(
            [('rule_group', '=', self[0].rule_group)])
        # TODO fix self[0] : it may not be the same on all ids in self
        model_exceptions = all_exceptions.filtered(
            lambda ex: ex.model == self._name)
        sub_exceptions = all_exceptions.filtered(
            lambda ex: ex.model != self._name)

        reverse_field = self._reverse_field()
        if reverse_field:
            optimize = True
        else:
            optimize = False

        exception_by_rec, exception_by_rule = self._detect_exceptions(
            model_exceptions, sub_exceptions, optimize)

        all_exception_ids = []
        for obj, exception_ids in exception_by_rec.iteritems():
            obj.exception_ids = [(6, 0, exception_ids)]
            all_exception_ids += exception_ids
        for rule, exception_ids in exception_by_rule.iteritems():
            rule[reverse_field] = [(6, 0, exception_ids.ids)]
            if exception_ids:
                all_exception_ids += [rule.id]
        return list(set(all_exception_ids))

    @api.model
    def _exception_rule_eval_context(self, obj_name, rec):
        return {obj_name: rec,
                'self': self.pool.get(rec._name),
                'object': rec,
                'obj': rec,
                'pool': self.pool,
                'env': self.env,
                'cr': self.env.cr,
                'uid': self.env.uid,
                'user': self.env.user,
                'time': time,
                # copy context to prevent side-effects of eval
                'context': self.env.context.copy()}

    @api.model
    def _rule_eval(self, rule, obj_name, rec):
        expr = rule.code
        space = self._exception_rule_eval_context(obj_name, rec)
        try:
            safe_eval(expr,
                      space,
                      mode='exec',
                      nocopy=True)  # nocopy allows to return 'result'
        except Exception, e:
            raise UserError(
                _('Error when evaluating the exception.rule '
                  'rule:\n %s \n(%s)') % (rule.name, e))
        return space.get('failed', False)

    @api.multi
    def _detect_exceptions(
            self, model_exceptions, sub_exceptions,
            optimize=False,
    ):
        """Find exceptions found on self.

        @returns
            exception_by_rec: (record_id, exception_ids)
            exception_by_rule: (rule_id, record_ids)
        """
        exception_by_rec = {}
        exception_by_rule = {}
        exception_set = set()
        python_rules = []
        dom_rules = []
        optim_rules = []

        for rule in model_exceptions:
            if rule.exception_type == 'by_py_code':
                python_rules.append(rule)
            elif rule.exception_type == 'by_domain' and rule.domain:
                if optimize:
                    optim_rules.append(rule)
                else:
                    dom_rules.append(rule)

        for rule in optim_rules:
            domain = rule._get_domain()
            domain.append(['ignore_exception', '=', False])
            domain.append(['id', 'in', self.ids])
            records_with_exception = self.search(domain)
            exception_by_rule[rule] = records_with_exception
            if records_with_exception:
                exception_set.add(rule.id)

        if len(python_rules) or len(dom_rules) or sub_exceptions:
            for rec in self:
                for rule in python_rules:
                    if (
                        not rec.ignore_exception and
                        self._rule_eval(rule, rec.rule_group, rec)
                    ):
                        exception_by_rec.setdefault(rec, []).append(rule.id)
                        exception_set.add(rule.id)
                for rule in dom_rules:
                    # there is no reverse many2many, so this rule
                    # can't be optimized, see _reverse_field
                    domain = rule._get_domain()
                    domain.append(['ignore_exception', '=', False])
                    domain.append(['id', '=', rec.id])
                    if self.search_count(domain):
                        exception_by_rec.setdefault(
                            rec, []).append(rule.id)
                        exception_set.add(rule.id)
                if sub_exceptions:
                    group_line = rec.rule_group + '_line'
                    for obj_line in rec._get_lines():
                        for rule in sub_exceptions:
                            if rule.id in exception_set:
                                # we do not matter if the exception as
                                # already been
                                # found for an line of this object
                                # (ex sale order line if obj is sale order)
                                continue
                            if rule.exception_type == 'by_py_code':
                                if self._rule_eval(
                                    rule, group_line, obj_line
                                ):
                                    exception_by_rec.setdefault(
                                        rec, []).append(rule.id)
                            elif (
                                rule.exception_type == 'by_domain' and
                                rule.domain
                            ):
                                # sub_exception are currently not optimizable
                                domain = rule._get_domain()
                                domain.append(('id', '=', obj_line.id))
                                if obj_line.search_count(domain):
                                    exception_by_rec.setdefault(
                                        rec, []).append(rule.id)
        return exception_by_rec, exception_by_rule

    @implemented_by_base_exception
    def _get_lines(self):
        pass

    def _default_get_lines(self):
        return []
