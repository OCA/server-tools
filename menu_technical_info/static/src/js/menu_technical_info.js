odoo.define('menu_technical_info', function (require) {
"use strict";

    var Menu = require('web.Menu');
    var data = require('web.data');

    Menu.include({
        start: function() {
            var self = this;
            var res = this._super.apply(this, arguments);
            this.debug = ($.deparam($.param.querystring()).debug !== undefined);
            this.$secondary_menus.find('[data-menu]').hover(function() {
                self.load_xml_id(this);
            });
            this.$el.find('a[data-menu]').hover(function() {
                self.load_xml_id(this);
            });
            return res;
        },
        load_xml_id: function(menu_item) {
            if(!this.debug) return;
            var $menu_item = $(menu_item);
            if($menu_item.is('[title]')) return;
            var id = $menu_item.data('menu');
            new data.DataSetSearch(this, 'ir.model.data', [], [['res_id', '=', id], ['model', '=', 'ir.ui.menu']]).read_slice().then(function(menu) {
                $menu_item.tooltip({
                    title: menu[0].module + '.' + menu[0].name
                }).tooltip('show');
            });
        }
    });
});
