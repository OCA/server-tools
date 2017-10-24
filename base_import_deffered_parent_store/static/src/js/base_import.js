odoo.define('base_import_deffered_parent_store.base_import', function (require) {
"use strict";

var BaseImport = require('base_import.import');
var DataImport = BaseImport.DataImport;

DataImport.include({

    import_options: function() {
        var self = this;
        var options = self._super.apply(self, arguments);
        var deffered_parent_store = self.$(
            'input#oe_import_defer_parent_store_computation'
        ).prop('checked');
        options = _.extend({
            defer_parent_store_computation: deffered_parent_store,
        }, options);
        return options;
    }

});

});
