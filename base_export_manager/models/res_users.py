# -*- coding: utf-8 -*-
# Copyright 2016 - Ursa Information Systems <http://ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from openerp import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def get_export_models(self):
        self.env.cr.execute("SELECT model "
                   "FROM ir_model "
                   "WHERE id IN ("
                   "    SELECT distinct(model_id) "
                   "    FROM ir_model_access "
                   "    WHERE perm_export=TRUE AND group_id IN ("
                   "        SELECT gid "
                   "        FROM res_groups_users_rel "
                   "        WHERE uid=%s"
                   "    )"
                   ")",
                   (self.env.uid,))
        model_names = [r[0] for r in self.env.cr.fetchall()]
        return model_names
