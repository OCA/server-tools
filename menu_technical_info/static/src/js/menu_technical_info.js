odoo.define('menu_technical_info.Menu', function (require) {
"use strict";
    var $ = require('$'),
        Menu = require('web.Menu'),
        Model = require('web.Model');

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
            var ir_model_data = new Model('ir.model.data');
            var id = $menu_item.data('menu');
            ir_model_data.query(['module', 'name']).filter([['res_id', '=', id],['model', '=', 'ir.ui.menu']]).first().then(function(menu) {
                $menu_item.tooltip({
                    title: menu.module + '.' + menu.name
                }).tooltip('show');
            });
        }
    });
});
