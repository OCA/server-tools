# -*- coding: utf-8 -*-
# Copyright 2012-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp.osv import fields as oldfields
from openerp import models
from openerp.addons.server_environment import serv_config


class PosConfig(models.Model):
    _inherit = 'pos.config'

    _columns = {
        'proxy_ip':  oldfields.function(
            # proxy the method w/ lambda to make it overridable
            lambda self, *a, **kw: self._compute_proxy_ip(*a, **kw),
            type='char',
            readonly=True,
        ),
    }

    def _get_config_vals(self, key, name=''):
        global_section_name = 'hardware_proxy'

        # default vals
        config_vals = {'proxy_ip': '', }
        if serv_config.has_section(global_section_name):
            config_vals.update((serv_config.items(global_section_name)))

        if name:
            custom_section_name = '.'.join((global_section_name, name))
            if serv_config.has_section(custom_section_name):
                config_vals.update(serv_config.items(custom_section_name))
        return config_vals.get(key, '')

    def _compute_proxy_ip(self, cr, uid, ids, fieldnames, args, context=None):
        res = {}.fromkeys(ids, '')
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = self._get_config_vals('proxy_ip', record.name)
        return res
