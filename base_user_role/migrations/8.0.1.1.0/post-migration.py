# -*- coding: utf-8 -*-
# Copyright 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, SUPERUSER_ID


def migrate_res_users_role(env):
    """Migrate user roles database schema.
    ('res_users_role_user_rel' many2many table to 'res.users.role.line' model.
    """
    role_line_model = env['res.users.role.line']
    query = "SELECT role_id, user_id FROM res_users_role_user_rel;"
    env.cr.execute(query)
    rows = env.cr.fetchall()
    for row in rows:
        vals = {
            'role_id': row[0],
            'user_id': row[1],
        }
        role_line_model.create(vals)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_res_users_role(env)
