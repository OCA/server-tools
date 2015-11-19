# -*- coding: utf-8 -*-
##############################################################################
#
#    (c) Daniel Reis 2014 - 2015
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp import exceptions
from openerp.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


class ActionRule(models.Model):
    "Base Action Rule extension"
    _inherit = 'base.action.rule'

    ruleset_id = fields.Many2one('base.action.ruleset', 'Ruleset')
    fact_ids = fields.Many2many(
        'base.action.fact',
        domain="[('model_id', 'in', (model_id, False))]",
        string='Condition Facts')
    filter_expr = fields.Char(
        'Python Condition',
        readonly=True,
        compute='_compute_filter_expr')
    runas_user_id = fields.Many2one(
        'res.users', 'Run as User')

    @api.multi
    @api.depends('fact_ids', 'fact_ids.filter_expr')
    def _compute_filter_expr(self):
        "Compute Python expression to evaluate from list of facts"
        get_fact_expr = lambda f: '(%s)' % f.filter_expr
        for rule in self:
            facts = rule.fact_ids.mapped(get_fact_expr)
            rule.filter_expr = ' and '.join(facts)
            # TODO: validate final expression?

    @api.model
    def _get_eval_contexts(self, record_ids, action, vals, old_vals):
        "Get list of eval contexts for the record_ids"
        Model = self.env[self.model_id.model]
        Fact = self.env['base.action.fact']
        old_vals = old_vals or {}
        res = [Fact.get_one_eval_context(rec, action, vals,
                                         old_vals.get(rec.id))
               for rec in Model.browse(record_ids)]
        return res

    @api.multi
    def _filter_eval_one(self, record_ids, action, vals=None, old_vals=None):
        """
        Filter a single Action for a list of record_ids
        It is expected to be called alongside _filter() and not inside it.
        Returns a list of Record objects
        """
        self.ensure_one()
        # Don't trigger disabled Action rules and Rulesets
        ruleset_disabled = self.ruleset_id and not self.ruleset_id.enabled
        if not self.active or ruleset_disabled:
            return list()

        # If no Facts to eval, step over (automatically trigger the rule)
        if not self.fact_ids:
            return record_ids

        old_vals = old_vals or dict()
        expr = self.filter_expr.replace('\n', ' ').strip()
        res = list()
        eval_dicts = self._get_eval_contexts(
            record_ids, action, vals, old_vals)
        for eval_dict in eval_dicts:
            rec = eval_dict['self']
            # Evaluate trigger expression
            # Don't use the "Run As" User when evaluating these filters
            # since we want to be able to query the User running the action
            eval_result = safe_eval(expr, eval_dict)
            if eval_result:
                res.append(rec.id)
                # TODO if rule debug activated, output more details
        return res

    @api.model
    def _process(self, action, record_ids):
        # Fixed: Add folllowers before assigning a responsible User
        # Otherwise followers won't be notified of the Assignment event
        _logger.debug(
            'Action Rule activated: %s on record %s.',
            action.name, repr(record_ids))
        if action.act_followers:
            model = self.env[action.model_id.model]
            if hasattr(model, 'message_subscribe'):
                follower_ids = map(int, action.act_followers)
                recs = model.browse(record_ids)
                recs.message_subscribe(follower_ids)
        # Run as a specifc user, if provided. Mind that that user
        # should have the security permissions to perform it's actions
        runas_user_id = action.runas_user_id or action.ruleset_id.runas_user_id
        if runas_user_id:
            self = self.sudo(runas_user_id)
        if not action.ruleset_id.silence_errors:
            super(ActionRule, self)._process(action, record_ids)
        else:
            # Error are silenced and reported to the server log
            try:
                super(ActionRule, self)._process(action, record_ids)
            except exceptions.Warning, e:
                raise exceptions.Warning(e)
            except Exception, e:  # Don't propagate to the user!
                # Should we rollback the transaction?
                # self.env.cr.rollback()
                _logger.error(e)
        return True

    # ~~~~~~~~~~
    # Copy of the original method from base_action_rule,
    # with only a few additions.
    # Changes made are between ``>>>>`` and ``<<<<`` blocks.
    #
    # TODO: stop being conservative and rewrite the thing?
    # TODO: "run as" feature not implemented for Cron jobs _check()
    # ~~~~~~~~~~
    def _register_hook(self, cr, ids=None):
        #
        # Note: the patched methods create and write must be defined inside
        # another function, otherwise their closure may be wrong. For instance,
        # the function create refers to the outer variable 'create', which you
        # expect to be bound to create itself. But that expectation is wrong if
        # create is defined inside a loop; in that case, the variable 'create'
        # is bound to the last function defined by the loop.
        #

        def make_create():
            """ instanciate a create method that processes action rules """
            def create(self, cr, uid, vals, context=None, **kwargs):
                # avoid loops or cascading actions
                if context and context.get('action'):
                    return create.origin(self, cr, uid, vals, context=context)

                # call original method with a modified context
                context = dict(context or {}, action=True)
                new_id = create.origin(
                    self, cr, uid, vals, context=context, **kwargs)

                # as it is a new record, we do not consider
                # the actions that have a prefilter
                action_model = self.pool.get('base.action.rule')
                action_dom = [
                    ('model', '=', self._name),
                    ('kind', 'in', ['on_create', 'on_create_or_write'])]
                action_ids = action_model.search(
                    cr, uid, action_dom, context=context)

                # check postconditions, and execute actions
                # on the records that satisfy them
                actions = action_model.browse(
                    cr, uid, action_ids, context=context)
                for action in actions:
                    if action_model._filter(cr, uid, action, action.filter_id,
                                            [new_id], context=context):
                        # >>>>
                        if action._filter_eval_one([new_id], 'create', vals):
                            # <<<<
                            action_model._process(
                                cr, uid, action, [new_id], context=context)
                return new_id

            return create

        def make_write():
            """ instanciate a write method that processes action rules """
            def write(self, cr, uid, ids, vals, context=None, **kwargs):
                # avoid loops or cascading actions
                if context and context.get('action'):
                    return write.origin(
                        self, cr, uid, ids, vals, context=context)

                # modify context
                context = dict(context or {}, action=True)
                ids = [ids] if isinstance(ids, (int, long, str)) else ids

                action_model = self.pool.get('base.action.rule')
                action_dom = [
                    ('model', '=', self._name),
                    ('kind', 'in', ['on_write', 'on_create_or_write'])]
                action_ids = action_model.search(
                    cr, uid, action_dom, context=context)
                actions = action_model.browse(
                    cr, uid, action_ids, context=context)

                # check preconditions
                pre_ids = {}
                for action in actions:
                    pre_ids[action] = action_model._filter(
                        cr, uid, action, action.filter_pre_id, ids,
                        context=context)

                # >>>> Old values
                get_row = lambda r: {f: getattr(r, f) for f in r._fields}
                old_recs = self.browse(cr, uid, ids, context=context)
                old_vals = {rec.id: get_row(rec) for rec in old_recs}
                # <<<< Old values

                # retrieve the action rules to possibly execute
                # call original method
                write.origin(
                    self, cr, uid, ids, vals, context=context, **kwargs)

                # check postconditions, and execute actions on the records
                # that satisfy them
                for action in actions:
                    post_ids = action_model._filter(
                        cr, uid, action, action.filter_id, pre_ids[action],
                        context=context)
                    # >>>> Added
                    post_ids = action._filter_eval_one(
                        post_ids, 'write', vals, old_vals)
                    # <<<<
                    if post_ids:
                        action_model._process(
                            cr, uid, action, post_ids, context=context)
                return True

            return write

        updated = False
        if ids is None:
            ids = self.search(cr, SUPERUSER_ID, [])
        for action_rule in self.browse(cr, SUPERUSER_ID, ids):
            model = action_rule.model_id.model
            model_obj = self.pool.get(model)
            if model_obj and not hasattr(model_obj, 'base_action_ruled'):
                # monkey-patch methods create and write
                model_obj._patch_method('create', make_create())
                model_obj._patch_method('write', make_write())
                model_obj.base_action_ruled = True
                updated = True

        return updated
