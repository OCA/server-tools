/* Copyright 2015 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define('base_export_manager.base_export_manager', function(require) {
    'use strict';
    
    var DataExport = require('web.DataExport');

    DataExport.include({
        do_load_export_field: function(field_list) {
            var export_node = this.$el.find("#fields_list");
            _(field_list).each(function (field) {
                export_node.append(new Option(field.label + ' (' + field.name + ')', field.name));
            });
        },
        add_field: function(field_id, string) {
            var field_list = this.$el.find('#fields_list');
            if (this.$el.find("#fields_list option[value='" + field_id + "']") &&
                !this.$el.find("#fields_list option[value='" + field_id + "']").length)
            {
                field_list.append(new Option(string + ' (' + field_id + ')', field_id));
            }
        },
    });
    
});
