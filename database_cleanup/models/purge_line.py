# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited

import logging

from odoo import api, fields, models
from odoo.exceptions import AccessDenied


class CleanupPurgeLine(models.AbstractModel):
    """Abstract base class for the purge wizard lines"""

    _name = "cleanup.purge.line"
    _order = "name"
    _description = "Purge Column Abstract Wizard"

    name = fields.Char(readonly=True)
    purged = fields.Boolean(readonly=True)
    wizard_id = fields.Many2one("cleanup.purge.wizard")

    logger = logging.getLogger("odoo.addons.database_cleanup")

    def purge(self):
        raise NotImplementedError

    @api.model_create_multi
    def create(self, values):
        # make sure the user trying this is actually supposed to do it
        if self.env.ref("base.group_erp_manager") not in self.env.user.group_ids:
            raise AccessDenied
        return super().create(values)
