# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of base_user_reset_access,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     base_user_reset_access is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     base_user_reset_access is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with base_user_reset_access.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, exceptions, _
from openerp.tools import SUPERUSER_ID


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def reset_access_right(self):
        self.ensure_one()
        if self.id == SUPERUSER_ID:
            raise exceptions.Warning(_("It's not possible to reset "
                                       "access right for Admin"))
        default_groups_ids = self._get_group()
        self.groups_id = [(6, 0, default_groups_ids)]
