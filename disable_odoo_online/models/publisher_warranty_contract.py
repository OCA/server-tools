# -*- coding: utf-8 -*-
# Copyright (C) 2013 Therp BV (<http://therp.nl>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class publisher_warranty_contract(models.AbstractModel):
    _inherit = 'publisher_warranty.contract'

    @api.multi
    def update_notification(self, cron_mode=True, context=None):
        pass
