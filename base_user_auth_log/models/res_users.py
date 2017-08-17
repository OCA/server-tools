# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, registry, SUPERUSER_ID
import logging
logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    auth_log_ids = fields.One2many(
        'res.users.auth.log', 'user_id', string='Authentication Logs')

    def authenticate(self, db, login, password, user_agent_env):
        user_id = super(ResUsers, self).authenticate(
            db, login, password, user_agent_env)
        cr = registry(db).cursor()
        try:
            vals = {
                'login': login,
                'result': 'failure',
                'date': fields.Datetime.now(),
                }
            if user_id:
                vals.update({'user_id': user_id, 'result': 'success'})
            elif login:
                user_ids = self.pool['res.users'].search(
                    cr, SUPERUSER_ID, [('login', '=', login)])
                if user_ids:
                    vals['user_id'] = user_ids[0]
            self.pool['res.users.auth.log'].create(
                cr, SUPERUSER_ID, vals, {'authenticate_create': True})
            cr.commit()
        except Exception, e:
            logger.warning('Failed to create auth log. Error: %s', e)
        finally:
            cr.close()
        return user_id
