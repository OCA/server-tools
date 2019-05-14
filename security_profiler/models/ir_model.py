# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models, tools
from odoo.tools import pycompat
from odoo.addons.base.ir.ir_model import _logger


def _check_action_profiled_user(env, uid, name, action, operation='python'):
    action_id = action.get('id')
    model = action.get('res_model') or ""
    user = env["res.users"].sudo().browse(uid)
    views = action.get('views')
    if user.is_profiled and model:
        session = user.active_session_id
        if 'res.users.profile' in model:
            return
        if operation == 'python':
            rec = env["res.users.profiler.actions"].sudo().search(
                ['&', '&', ('session_id', '=', session.id),
                 ('res_model', '=', model),
                 ('method_name', '=', name + '()'),
                 ], limit=1)
        else:
            rec = env["res.users.profiler.actions"].sudo().search(
                ['&', '&', '&', ('session_id', '=', session.id),
                 ('res_model', '=', model),
                 ('action_type', '=', operation),
                 ('action_name', '=', name),
                 ], limit=1)
        if rec:
            value = rec.count_action or 0
            rec.sudo().write({
                'count_action': value + 1,
            })
        else:
            values = {
                'session_id': session.id,
                'user_id': uid,
                'res_model': model,
                'count_action': 1,
            }
            if operation == 'python':
                values['method_name'] = name + '()'
            else:
                values['action_name'] = name
                values['action_type'] = operation
            if action_id:
                values['action_id'] = action_id
            if views:
                for view in views:
                    view_id = view[0]
                    if view_id:
                        values['view_id'] = view_id
                        break
            env["res.users.profiler.actions"].sudo().create(values)


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.multi
    def get_formview_action(self, access_uid=None):
        action = super(Base, self).get_formview_action(access_uid=access_uid)
        user = self.env["res.users"].sudo().browse(self._uid)
        if user.is_profiled:
            name = 'get_formview_action'
            _check_action_profiled_user(self.env, self._uid, name, action)
        return action


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode',
                            'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        if self._uid == 1:
            return True
        user = self.env["res.users"].sudo().browse(self._uid)
        if user.is_profiled and raise_exception:
            session = user.active_session_id

            assert isinstance(model, pycompat.string_types),\
                'Not a model name: %s' % (model,)
            assert mode in ('read', 'write', 'create', 'unlink'),\
                'Invalid access mode'

            if 'res.users.profile' in model:
                return True

            if model not in self.env:
                _logger.error('Missing model %s', model)
            elif self.env[model].is_transient():
                return True

            # pylint: disable=E8103
            self._cr.execute(
                """
                SELECT a.id
                FROM ir_model_access a
                JOIN ir_model m ON (m.id = a.model_id)
                JOIN res_groups_users_rel gu ON (gu.gid = a.group_id)
                WHERE m.model = %s
                    AND gu.uid = %s
                    AND a.active IS TRUE
                    AND a.perm_{mode}
                """.format(mode=mode),
                (model, self._uid,))
            access_ids_1 = [a[0] for a in self._cr.fetchall() if a]

            # pylint: disable=E8103
            self._cr.execute(
                """
                SELECT a.id
                FROM ir_model_access a
                JOIN ir_model m ON (m.id = a.model_id)
                WHERE a.group_id IS NULL
                    AND m.model = %s
                    AND a.active IS TRUE
                    AND a.perm_{mode}
                """.format(mode=mode),
                (model,))
            access_ids_2 = [a[0] for a in self._cr.fetchall() if a]

            access_ids = access_ids_1 + access_ids_2

            for access_id in access_ids:
                profiler_accesses_model = \
                    self.env["res.users.profiler.accesses"]
                rec = profiler_accesses_model.sudo().search(
                    ['&', '&', ('session_id', '=', session.id),
                     ('model_access_id', '=', access_id),
                     ('res_model', '=', model)], limit=1)
                if rec:
                    value = getattr(rec, 'count_' + mode) or 0
                    rec.sudo().write({
                        'count_' + mode: value + 1,
                    })
                else:
                    values = {
                        'session_id': session.id,
                        'user_id': self._uid,
                        'model_access_id': access_id,
                        'res_model': model,
                        'count_' + mode: 1,
                    }
                    profiler_accesses_model.sudo().create(values)
        return super(IrModelAccess, self).check(
            model=model, mode=mode, raise_exception=raise_exception)
