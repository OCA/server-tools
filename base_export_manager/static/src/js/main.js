/**
 * # -*- coding: utf-8 -*-
 * ##############################################################################
 * #
 * #    OpenERP, Open Source Management Solution
 * #    This module copyright :
 * #        (c) 2014 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
 * #                 Antonio Espinosa <antonioea@antiun.com>
 * #
 * #    This program is free software: you can redistribute it and/or modify
 * #    it under the terms of the GNU Affero General Public License as
 * #    published by the Free Software Foundation, either version 3 of the
 * #    License, or (at your option) any later version.
 * #
 * #    This program is distributed in the hope that it will be useful,
 * #    but WITHOUT ANY WARRANTY; without even the implied warranty of
 * #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * #    GNU Affero General Public License for more details.
 * #
 * #    You should have received a copy of the GNU Affero General Public License
 * #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * #
 * ##############################################################################
 */

// Check jQuery available
if (typeof jQuery === 'undefined') { throw new Error('Requires jQuery') }

+function ($) {
    'use strict';

    openerp.base_exports_manager = function(instance, local) {
        var _t = instance.web._t,
            _lt = instance.web._lt;
        var QWeb = instance.web.qweb;

        instance.web.DataExport.include({
            do_load_export_field: function(field_list) {
                var export_node = this.$el.find("#fields_list");
                _(field_list).each(function (field) {
                    export_node.append(new Option(field.label + ' (' + field.name + ')', field.name));
                });
            },
            add_field: function(field_id, string) {
                var field_list = this.$el.find('#fields_list');
                if (this.$el.find("#fields_list option[value='" + field_id + "']")
                        && !this.$el.find("#fields_list option[value='" + field_id + "']").length) {
                    field_list.append(new Option(string + ' (' + field_id + ')', field_id));
                }
            },
        });
    }

}(jQuery);
