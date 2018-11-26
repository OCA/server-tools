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
    active = fields.Boolean('Active')
    code = fields.Text(
        'Python Code',
        help="Python code executed to check if the exception apply or "
             "not. The code must apply block = True to apply the "
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
    def detect_exceptions(self):
        """returns the list of exception_ids for all the considered base.exceptions
        """
        if not self:
            return []
        exception_obj = self.env['exception.rule']
        all_exceptions = exception_obj.sudo().search(
            [('rule_group', '=', self[0].rule_group)])
        model_exceptions = all_exceptions.filtered(
            lambda ex: ex.model == self._name)
        sub_exceptions = all_exceptions.filtered(
            lambda ex: ex.model != self._name)

        all_exception_ids = []
        for obj in self:
            if obj.ignore_exception:
                continue
            exception_ids = obj._detect_exceptions(
                model_exceptions, sub_exceptions)
            obj.exception_ids = [(6, 0, exception_ids)]
            all_exception_ids += exception_ids
        return all_exception_ids

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
    def _detect_exceptions(self, model_exceptions,
                           sub_exceptions):
        self.ensure_one()
        exception_ids = []
        for rule in model_exceptions:
            if self._rule_eval(rule, self.rule_group, self):
                exception_ids.append(rule.id)
        if sub_exceptions:
            for obj_line in self._get_lines():
                for rule in sub_exceptions:
                    if rule.id in exception_ids:
                        # we do not matter if the exception as already been
                        # found for an line of this object
                        # (ex sale order line if obj is sale order)
                        continue
                    group_line = self.rule_group + '_line'
                    if self._rule_eval(rule, group_line, obj_line):
                        exception_ids.append(rule.id)
        return exception_ids

    @implemented_by_base_exception
    def _get_lines(self):
        pass

    def _default_get_lines(self):
        return []
