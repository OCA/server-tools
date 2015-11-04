# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields


class ir_module_module(osv.osv):
    _inherit = 'ir.module.module'

    def compute_stats(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        model_pool = self.pool['ir.model']

        model_ids = model_pool.search(cr, uid, [])
        model_data = model_pool.read(cr, uid, model_ids, ['modules'])
        model_modules = {m['id']: map(unicode.strip, m['modules'].split(','))
                         for m in model_data}

        module_models = {}
        for model, modules in model_modules.items():
            for module in modules:
                if module not in module_models:
                    module_models[module] = []
                module_models[module].append(model)

        for module in self.browse(cr, uid, ids, context=context):
            model_stats = model_pool.read(cr, uid,
                                          module_models.get(module.name, []),
                                          ['stat_bytes',
                                           'stat_count',
                                           'stat_count_data'])

            res[module.id] = {
                'stat_bytes': sum(m['stat_bytes'] for m in model_stats),
                'stat_count': sum(m['stat_count'] for m in model_stats),
                'stat_count_data': sum(m['stat_count_data']
                                       for m in model_stats),
                'stat_dsd': len(module.downstream_dependencies()),
            }
            if (lambda m: (m['stat_count'] - m['stat_count_data']) == 0 and
                not m['stat_dsd'])(
                    res[module.id]):
                res[module.id]['stat_status'] = 'removable'
            elif (lambda m: m['stat_count'] - m['stat_count_data'] < 0
                  )(res[module.id]):
                res[module.id]['stat_status'] = 'broken'
            else:
                res[module.id]['stat_status'] = 'normal'

            pass

        return res

    _columns = {
        'stat_bytes': fields.function(
            compute_stats,
            string="Size in bytes",
            type="integer",
            multi="stats"),
        'stat_count': fields.function(
            compute_stats,
            string="Number of rows",
            type="integer",
            multi="stats"),
        'stat_count_data': fields.function(
            compute_stats,
            string="Number of data",
            type="integer",
            multi="stats"),
        'stat_dsd': fields.function(
            compute_stats,
            string="Number dependencies",
            type="integer",
            multi="stats"),
        'stat_status': fields.function(
            compute_stats,
            string="Status",
            type="selection",
            selection=[('removable', 'Removable'),
                       ('broken', 'Broken'),
                       ('normal', 'Normal')],
            multi="stats"),
    }
