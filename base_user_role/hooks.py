# coding: utf-8
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openerp import api, SUPERUSER_ID


def post_init_hook(cr, pool):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.groups'].update_user_groups_view()
