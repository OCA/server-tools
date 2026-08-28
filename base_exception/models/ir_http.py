# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.api import Environment
from odoo.fields import Command
from odoo.http import request
from odoo.modules.registry import Registry

from ..exceptions import BaseExceptionError


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _dispatch(cls, endpoint):
        res = None
        # FIXME: Find a way to condition the creation of new transaction
        #  only for requests that may trigger an exception rule
        #  ie exclude whatever goes to bus, websocket, getting views, etc
        old_env = request.env
        to_add = {}
        to_remove = {}
        with Registry(old_env.cr.dbname).cursor() as new_cr:
            new_env = Environment(new_cr, old_env.uid, old_env.context)
            request.env = new_env
            try:
                res = super()._dispatch(endpoint)
            except BaseExceptionError as err:
                to_add = err.rules_to_add
                to_remove = err.rules_to_remove
                new_env.cr.rollback()

        for rule_id, (model, res_ids) in to_remove.items():
            old_env[model].browse(res_ids).write(
                {"exception_ids": [Command.unlink(rule_id)]}
            )
        for rule_id, (model, res_ids) in to_add.items():
            old_env[model].browse(res_ids).write(
                {"exception_ids": [Command.link(rule_id)]}
            )

        request.env = old_env
        return res
