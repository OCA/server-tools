// License, author and contributors information in:
// __openerp__.py file at the root folder of this module.

openerp.base_import_security_group = function (instance) {
    instance.web.ListView.include({
        load_list: function () {
            var self = this;
            this._super.apply(self, arguments);
            new openerp.web.Model('res.users').call('has_group', ['base_import_security_group.group_import_csv'])
                .then(function (import_enabled) {
                    self.options.import_enabled = import_enabled;
                    if (import_enabled) {
                        self.$buttons.find('span.oe_alternative').show();
                    }
                });
        }
    });
};
