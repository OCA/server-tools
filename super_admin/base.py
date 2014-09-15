# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import SUPERUSER_ID


def name_selection_groups(ids):
    return 'sel_groups_' + '_'.join(map(str, ids))


def name_boolean_group(id):
    return 'in_group_' + str(id)


class res_users(osv.osv):
    _inherit = 'res.users'

    def add_user_to_group(self, cr, context=None):
        if context is None:
            context = {}
        try:
            for app, kind, gs in self.pool.get(
                'res.groups').get_groups_by_application(
                    cr, 1):
                try:
                    if kind == 'selection':
                        self.write(cr, SUPERUSER_ID, [SUPERUSER_ID], {
                            name_selection_groups(map(int, gs)): gs[-1].id})
                    else:
                        for g in gs:
                            self.write(
                                cr, SUPERUSER_ID,
                                [SUPERUSER_ID],
                                {name_boolean_group(g.id): True})
                except:
                    continue
        except:
            pass

    def init(self, cr):
        self.add_user_to_group(cr)
res_users()


class module(osv.osv):
    _inherit = "ir.module.module"

    def button_immediate_install(self, cr, uid, ids, context=None):
        res = super(module, self).button_immediate_install(cr, uid, ids,
                                                           context=context)
        self.add_user_to_group(cr)

        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
