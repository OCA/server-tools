// License, author and contributors information in:
// __openerp__.py file at the root folder of this module.

openerp.base_import_csv_optional = function (instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var _lt = instance.web._lt;

    instance.web.ListView.prototype.defaults.import_enabled = false;
    base_import_csv_optional = instance.web.ListView.include({
        load_list: function () {
            var self = this;
            var Users = new openerp.web.Model('res.users');

            self._super.apply(self, arguments);

            Users.call('has_group', ['base_import_csv_optional.group_import_csv'])
                .then(function (result) {
                    var import_enabled = result;
                    self.options.import_enabled = import_enabled;

                    if (import_enabled) {
                        if (self.$buttons) {
                            self.$buttons.remove();
                        }
                        self.$buttons = $(QWeb.render("ListView.buttons", {'widget': self}));
                        if (self.options.$buttons) {
                            self.$buttons.appendTo(self.options.$buttons);
                        } else {
                            self.$el.find('.oe_list_buttons').replaceWith(self.$buttons);
                        }
                        self.$buttons.find('.oe_list_add')
                                .click(self.proxy('do_add_record'))
                                .prop('disabled', self.grouped);

                        self.$buttons.on('click', '.oe_list_button_import', function () {
                            self.do_action({
                                type: 'ir.actions.client',
                                tag: 'import',
                                params: {
                                    model: self.dataset.model,
                                    // self.dataset.get_context() could be a compound?
                                    // not sure. action's context should be evaluated
                                    // so safer bet. Odd that timezone & al in it
                                    // though
                                    context: self.getParent().action.context
                                }
                            }, {
                                on_reverse_breadcrumb: function () {
                                    self.reload();
                                }
                            });
                            return false;
                        });
                    }
                });
        }
    });
};
