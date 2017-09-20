# coding: utf-8
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.groups'].update_user_groups_view()
