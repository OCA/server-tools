/* Copyright 2017 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define('base_export_security', function(require){
    'use strict';

    var Model = require('web.Model');
    var ListView = require('web.ListView');
    var core = require('web.core');

    ListView.include({
        render_sidebar: function($node) {
            var exportLabel = core._t('Export');
            var users = new Model('res.users');
            var res = this._super($node);

            if (this.sidebar && Object.prototype.hasOwnProperty.call(this.sidebar.items, 'other')) {
                users.call('has_group', ['base_export_security.export_group']).then(function(result){
                    if(!result){
                        var filteredItems = this.sidebar.items.other.filter(
                            function(item){
                                return item.label !== exportLabel;
                            }
                        );
                        this.sidebar.items.other = filteredItems;
                        this.sidebar.redraw();
                    }
                }.bind(this));
            }

            return res;
        }
    });

});
