# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.ir.ir_values import ACTION_SLOTS, EXCLUDED_FIELDS
from odoo import api, models, fields, tools, _
from odoo.exceptions import AccessError, MissingError


class IrValues(models.Model):
    _inherit = 'ir.values'

    groups_id = fields.Many2many('res.groups', string="Groups")

    @api.model
    @tools.ormcache_context(
        'self._uid', 'action_slot', 'model', 'res_id', keys=('lang',)
    )
    def get_actions(self, action_slot, model, res_id=False):
        assert action_slot in ACTION_SLOTS,\
            'Illegal action slot value: %s' % action_slot
        # use a direct SQL query for performance reasons,
        # this is called very often
        query = """ SELECT v.id, v.name, v.value FROM ir_values v
                    WHERE v.key = %s AND v.key2 = %s AND v.model = %s
                        AND (v.res_id = %s OR v.res_id IS NULL OR v.res_id = 0)
                    ORDER BY v.id """
        self._cr.execute(query, ('action', action_slot, model, res_id or None))

        # map values to their corresponding action record
        actions = []
        for value_id, name, value in self._cr.fetchall():
            if not value:
                continue                # skip if undefined
            action_model, action_id = value.split(',')
            if action_model not in self.env:
                continue                # unknown model? skip it!
            action = self.env[action_model].browse(int(action_id))
            # --------- OVERWRITE (start) --------
            try:
                record = self.env['ir.values'].browse([value_id])
                record.check_access_rule('read')
                actions.append((value_id, name, action))
            except AccessError:
                continue
            # --------- OVERWRITE (stop) --------

        # process values and their action
        results = {}
        for action_id, name, action in actions:
            action_fields = [
                field for field in action._fields
                if field not in EXCLUDED_FIELDS
            ]
            try:
                action_def = {
                    field: action._fields[field].convert_to_read(
                        action[field], action
                    )
                    for field in action_fields
                }
                if action._name in (
                        'ir.actions.report.xml', 'ir.actions.act_window'
                ):
                    if (
                            action.groups_id
                            and not action.groups_id & self.env.user.groups_id
                    ):
                        if name == 'Menuitem':
                            raise AccessError(
                                _(
                                    'You do not have the permission to '
                                    'perform this operation!!!'
                                )
                            )
                        continue
                # keep only the last action registered for each action name
                results[name] = (action_id, name, action_def)
            except (AccessError, MissingError):
                continue
        return sorted(results.values())
