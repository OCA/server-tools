odoo.define("base_changeset.relational_fields", function(require) {
    "use strict";

    var RelationalFields = require("web.relational_fields");

    RelationalFields.FieldX2Many.include({
        _render: function() {
            var res = this._super.apply(this, arguments);
            if (res instanceof Promise) {
                res.then(this._updateChangeset.bind(this));
            } else {
                this._updateChangeset.bind(this);
            }
            return res;
        },

        _updateChangeset: function() {
            var self = this;
            if (this.renderer.viewType === "list") {
                var model = this.value.model;
                return self
                    ._rpc({
                        model: "record.changeset.change",
                        method: "get_fields_changeset_changes",
                        args: [model, false],
                    })
                    .then(function(changeset) {
                        var res = {};
                        _.each(changeset, function(changesetChange) {
                            if (!_.contains(_.keys(res), changesetChange.field_name)) {
                                res[changesetChange.field_name] = [];
                            }
                            res[changesetChange.field_name].push(changesetChange);
                        });
                        self.renderer.renderChangesetPopovers(res);
                    });
            }
        },

        applyChange: function(id) {
            var self = this;
            return this._rpc({
                model: "record.changeset.change",
                method: "apply",
                args: [[id]],
                context: _.extend({}, this.context, {set_change_by_ui: true}),
            }).then(function() {
                self.trigger_up("reload");
            });
        },

        rejectChange: function(id) {
            var self = this;
            return this._rpc({
                model: "record.changeset.change",
                method: "cancel",
                args: [[id]],
                context: _.extend({}, this.context, {set_change_by_ui: true}),
            }).then(function() {
                self._render();
            });
        },
    });
});
