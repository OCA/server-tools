openerp.defer_parent_store_computation_import = function (instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var _lt = instance.web._lt;

    instance.web.DataImport.include({
        import_options: function () {
            var options = this._super.apply(this, arguments);
            options['defer'] =  this.$('input.oe_import_use_deferred_store_computation').prop('checked')
            return options;
        },
    });

};

