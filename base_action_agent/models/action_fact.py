# -*- coding: utf-8 -*-
##############################################################################
#
#    (c) Daniel Reis 2015
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

from datetime import datetime, timedelta
import dateutil
from openerp import models, fields, api, exceptions
from openerp.tools.safe_eval import safe_eval


class ActionFact(models.Model):
    _name = 'base.action.fact'
    _order = 'sequence'

    sequence = fields.Integer(default=100, index=True)
    name = fields.Char(required=True)
    model_id = fields.Many2one('ir.model', 'Model')
    filter_expr = fields.Text(
        'Evaluated expression',
        required=True,
        help='Python expression, able to use a "new" and "old" '
             'dictionaries, with the changed columns.')
    note = fields.Text('Description')
    # TODO support parent/child facts, for complex nested calculations
    # TODO usage count

    @api.model
    def get_one_eval_context(self, new_rec=None, action=None,
                             vals=None, old_row=None):
        "Return an Evaluation context dict"
        if not old_row:
            old_row = {}
        creating = action == 'create'
        writing = action == 'write'
        old_row = old_row or {}
        if new_rec is None and self.model_id:
            new_rec = self.env[self.model_id.model]
        old = lambda f, d=None: old_row.get(f, d)
        new = lambda f, d=None: getattr(new_rec, f, d)
        chg = lambda f: repr(old(f)) != repr(new(f))
        changed = lambda *ff: any(chg(f) for f in ff)
        changed_to = lambda f: chg(f) and new(f)
        return {
            'self': new_rec,  # allows object.notation
            'obj': new_rec,
            'env': self.env,
            'context': self.env.context,
            'user': self.env.user,
            'old': old,
            'new': new,
            'vals': vals or dict(),
            'changed': changed,
            'changed_to': changed_to,
            'creating': creating,
            'inserting': creating,
            'writing': writing,
            'updating': writing,
            'dateutil': dateutil,
            'datetime': datetime,
            'timedelta': timedelta,
            'Date': fields.Date,
            'Datetime': fields.Datetime,
        }

    @api.multi
    @api.constrains('filter_expr')
    def _check_filter_expr(self):
        eval_ctx = self.get_one_eval_context()
        for fact in self.filtered('filter_expr'):
            try:
                safe_eval(fact.filter_expr, {}, eval_ctx)
            except:
                raise exceptions.ValidationError(
                    '%s: Invalid evaluated expression «%s»'
                    % (fact.name, fact.filter_expr))
