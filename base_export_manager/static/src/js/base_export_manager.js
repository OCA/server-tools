/* Copyright 2015 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define('base_export_manager.base_export_manager', function(require) {
    'use strict';

    var jQuery = require('$');
    var DataExport = require('web.DataExport');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var ListView = require('web.ListView');
    var Sidebar = require('web.Sidebar');
    var _t = core._t;
    var Session = require('web.Session');


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


    Session.include({
        get_export_models: function() {
            if (!this.uid) {
                return $.when().resolve(false);
            }
            var Users = new Model('res.users');
            var export_models = Users.call('get_export_models', []);
            return export_models;
        },
    });

    ListView.include({
        view_loading: function(fvg) {
            this._super(fvg);
            this.is_export_manager();
        },
        is_export_manager: function () {
            var self = this;
            $.when(Session.get_export_models()).then(function
            (export_models) {
                self.export_models=export_models;
            });
        },
        /**
         * Instantiate and render the sidebar.
         * Sets this.sidebar
         * @param {jQuery} [$node] a jQuery node where the sidebar should be inserted
         * $node may be undefined, in which case the ListView inserts the sidebar in
         * this.options.$sidebar or in a div of its template
         **/
        render_sidebar: function($node) {
            var self = this;
            self.render_export_enable = jQuery.inArray( this.model, self.export_models );
            if (!this.sidebar && this.options.sidebar) {
                this.sidebar = new Sidebar(this, {editable: this.is_action_enabled('edit')});
                if (this.fields_view.toolbar) {
                    this.sidebar.add_toolbar(this.fields_view.toolbar);
                }
                this.sidebar.add_items('other', _.compact([
                    self.render_export_enable >= 0 && {label: _t("Export"), callback: this.on_sidebar_export},
                    this.fields_view.fields.active && {label: _t("Archive"), callback: this.do_archive_selected},
                    this.fields_view.fields.active && {label: _t("Unarchive"), callback: this.do_unarchive_selected},
                    this.is_action_enabled('delete') && {label: _t('Delete'), callback: this.do_delete_selected}
                ]));

                $node = $node || this.options.$sidebar;
                this.sidebar.appendTo($node);

                // Hide the sidebar by default (it will be shown as soon as a record is selected)
                this.sidebar.do_hide();
            }
        },
    });

});
