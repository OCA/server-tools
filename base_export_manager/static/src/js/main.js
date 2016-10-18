/* © 2015 Antiun Ingeniería S.L. - Antonio Espinosa
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html). */

// Check jQuery available
if (typeof jQuery === 'undefined') { throw new Error('Requires jQuery'); }

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
                if (this.$el.find("#fields_list option[value='" + field_id + "']") &&
                        !this.$el.find("#fields_list option[value='" + field_id + "']").length) {
                    field_list.append(new Option(string + ' (' + field_id + ')', field_id));
                }
            },
        });
    };

}(jQuery);
