# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, exceptions, _
from odoo.tools import SUPERUSER_ID


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def reset_access_right(self):
        self.ensure_one()
        if self.id == SUPERUSER_ID:
            raise exceptions.Warning(_("It's not possible to reset "
                                       "access right for Admin"))
        self.groups_id = self._default_groups()
