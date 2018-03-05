# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


import logging
_logger = logging.getLogger(__name__)


class OnchangeMixin(models.AbstractModel):
    _name = 'onchange.mixin'
    _description = "Abstract model allowing to hook onchange method"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(OnchangeMixin, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        return (self.env['onchange.rule']
                ._customize_view_according_to_setting_rule(
                    res, view_type, self))

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        res = super(OnchangeMixin, self).onchange(
            values, field_name, field_onchange)
        res = self.env['onchange.rule']._update_onchange_values(
            self._name, values, res, field_name)
        return res
