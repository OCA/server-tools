# Copyright 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import time
from functools import wraps
from odoo import api, fields, models, _
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
    _description = 'Exception Rule'
    _order = 'active desc, sequence asc'

    name = fields.Char('Exception Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer(
        string='Sequence',
        help="Gives the sequence order when applying the test",
    )
    rule_group = fields.Selection(
        selection=[],
        help="Rule group is used to group the rules that must validated "
        "at same time for a target object. Ex: "
        "validate sale.order.line rules with sale order rules.",
        required=True,
    )
    model = fields.Selection(selection=[], string='Apply on', required=True)

    type = fields.Selection(
        selection=[('by_domain', 'By domain'),
                   ('by_py_code', 'By Python Code')],
        string='Exception Type', required=True)
    domain = fields.Char('Domain')

    active = fields.Boolean('Active')
    next_state = fields.Char(
        'Next state',
        help="If we detect exception we set the state of object (ex purchase) "
             "to the next_state (ex 'to approve'). If there are more than one "
             "exception detected and all have a value for next_state, we use"
             "the exception having the smallest sequence value",
    )
    code = fields.Text(
        'Python Code',
        help="Python code executed to check if the exception apply or "
             "not. Use failed = True to block the exception",
        )

    @api.constrains('next_state')
    def _check_next_state_value(self):
        """ Ensure that the next_state value is in the state values of
        destination model  """
        for rule in self:
            if rule.next_state:
                select_vals = self.env[
                    rule.model].fields_get()[
                        'state']['selection']
                select_vals_code = [s[0] for s in select_vals]
                if rule.next_state not in select_vals_code:
                    raise ValidationError(_(
                        'The value "%s" you choose for the "next state" '
                        'field state of "%s" is wrong.'
                        ' Value must be in this list %s'
                        ) % (
                            rule.next_state,
                            rule.model,
                            select_vals
                        ))

    @api.multi
    def _get_domain(self):
        """ override me to customize domains according exceptions cases """
        self.ensure_one()
        return safe_eval(self.domain)

    @api.onchange('type',)
    def onchange_type(self):
        if self.type == 'by_domain':
            self.code = False
        elif self.type == 'by_py_code':
            self.domain = False


class BaseException(models.AbstractModel):
    _name = 'base.exception'
    _order = 'main_exception_id asc'
    _description = 'Exception'

    main_exception_id = fields.Many2one(
        'exception.rule',
        compute='_compute_main_error',
        string='Main Exception',
        store=True,
    )
    rule_group = fields.Selection([], readonly=True)
    exception_ids = fields.Many2many('exception.rule', string='Exceptions')
    ignore_exception = fields.Boolean('Ignore Exceptions', copy=False)

    @api.depends('exception_ids', 'ignore_exception')
    def _compute_main_error(self):
        for rec in self:
            if not rec.ignore_exception and rec.exception_ids:
                rec.main_exception_id = rec.exception_ids[0]
            else:
                rec.main_exception_id = False

    @api.multi
    def _popup_exceptions(self):
        action = self._get_popup_action().read()[0]
        action.update({
            'context': {
                'active_id': self.ids[0],
                'active_ids': self.ids,
                'active_model': self._name,
            }
        })
        return action

    @api.model
    def _get_popup_action(self):
        return self.env.ref('base_exception.action_exception_rule_confirm')

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
        import pdb; pdb.set_trace()
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
        return {
            'time': time,
            'self': rec,
            # obj_name, object, obj: deprecated.
            # should be removed in future migrations
            obj_name: rec,
            'object': rec,
            'obj': rec,
            # copy context to prevent side-effects of eval
            # should be deprecated too, accesible through self.
            'context': self.env.context.copy()
        }

    @api.model
    def _rule_eval(self, rule, obj_name, rec):
        eval_ctx = self._exception_rule_eval_context(obj_name, rec)
        try:
            safe_eval(rule.code, eval_ctx, mode='exec', nocopy=True)
        except Exception as e:
            raise UserError(_(
                'Error when evaluating the exception.rule: '
                '%s\n(%s)') % (rule.name, e))
        return eval_ctx.get('failed', False)

    @api.multi
    def _detect_exceptions(self, model_exceptions, sub_exceptions):
        self.ensure_one()
        import pdb; pdb.set_trace()
        exception_ids = []
        next_state_rule = False
        for rule in model_exceptions:
            if rule.type == 'by_py_code' and self._rule_eval(
                    rule, self.rule_group, self):
                exception_ids.append(rule.id)

            elif rule.type == 'by_domain' and rule.domain:
                domain = rule._get_domain()
                domain.append(('id', '=', self.id))
                if self.search(domain):
                    exception_ids.append(rule.id)
                    
            if rule.next_state:
                if not next_state_rule or \
                        rule.sequence < next_state_rule.sequence:
                    next_state_rule = rule

        if sub_exceptions:
            for obj_line in self._get_lines():
                for rule in sub_exceptions:
                    if rule.id in exception_ids:
                        # we do not matter if the exception as already been
                        # found for an line of this object
                        # (ex sale order line if obj is sale order)
                        continue
                    group_line = self.rule_group + '_line'
                    if rule.type == 'by_py_code' and self._rule_eval(
                            rule, group_line, obj_line):
                        exception_ids.append(rule.id)
                    elif rule.type == 'by_domain' and rule.domain:
                        domain = rule._get_domain()
                        domain.append(('id', '=', obj_line.id))
                        if obj_line.search(domain):
                            exception_ids.append(rule.id)

        # set object to next state
        if next_state_rule:
            self.state = next_state_rule.next_state
        return exception_ids

    @implemented_by_base_exception
    def _get_lines(self):
        pass

    def _default_get_lines(self):
        return []
