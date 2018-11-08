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
    def _detect_exceptions(
            self, model_exceptions, sub_exceptions,
            optimize=False,
    ):
        """Find exceptions found on self.

        @returns
            exception_by_rec: {record_id: exception_ids}
            exception_by_rule: {rule_id: record_ids}
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

        # set object to next state
        # find exception that raised error and has next_state
        next_state_exception_ids = model_exceptions.filtered(
            lambda r: r.id in exception_set and r.next_state)

        if next_state_exception_ids:
            self.state = next_state_exception_ids[0].next_state

        return exception_by_rec, exception_by_rule

    @implemented_by_base_exception
    def _get_lines(self):
        pass

    def _default_get_lines(self):
        return []
