/* Copyright 2015 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define('base_export_manager.base_export_manager', function(require) {
    'use strict';

    var core = require('web.core');
    var Model = require('web.DataModel');
    var ListView = require('web.ListView');
    var Sidebar = require('web.Sidebar');
    var _t = core._t;

    ListView.include({
        /**
         * Instantiate and render the sidebar.
         * Sets this.sidebar
         * @param {jQuery} [$node] a jQuery node where the sidebar should be inserted
         * $node may be undefined, in which case the ListView inserts the sidebar in
         * this.options.$sidebar or in a div of its template
         **/
        render_sidebar: function($node) {
            var self = this;
            this._super($node);
            var Users = new Model('res.users');
            Users.call('fetch_export_models', []).done(function(export_models){
                self.export_models = export_models;
                self.render_export_enable = jQuery.inArray( self.model, self.export_models );
                    if(self.sidebar && self.sidebar.items && self.sidebar.items.other){
                        var items_data = [];
                        _.each(self.sidebar.items.other,function(rec){
                            if(rec.label != _t("Export")){
                                items_data.push(rec);
                            }
                        });
                        self.sidebar.items.other = items_data;
                        self.sidebar.add_items('other', _.compact([
                            self.render_export_enable >= 0 && {
                                label: _t("Export"),
                                callback: self.on_sidebar_export
                            },
                        ]));
                     }
            });
        },
    });
});
