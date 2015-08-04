# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015 bloopark systems (<http://bloopark.de>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import api, tools
from openerp.osv import osv


class ResUsers(osv.osv):
    _inherit = "res.users"

    @tools.ormcache(skiparg=2)
    @api.model
    def has_group(self, group_ext_id):
        """Checks whether user belongs to given group.

        :param str group_ext_id: external ID (XML ID) of the group.
        Must be provided in fully-qualified form (``module.ext_id``), as there
        is no implicit module to use..
        :return: True if the current user is a member of the group with the
        given external ID (XML ID), else False.
        """
        assert group_ext_id and '.' in group_ext_id,\
            "External ID must be fully qualified"
        module, ext_id = group_ext_id.split('.')
        print group_ext_id
        negation = False
        if module.startswith('not'):
            negation = True
            module = module[4:]

        self._cr.execute(
            """SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid IN
(SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s)""",
            (self._uid, module, ext_id))
        tmp = bool(self._cr.fetchone())

        if negation:
            tmp = not tmp

        return tmp
