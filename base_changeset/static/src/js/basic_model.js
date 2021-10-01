odoo.define("base_changeset.basic_model", function(require) {
    "use strict";

    var BasicModel = require("web.BasicModel");

    BasicModel.include({
        applyChange: function(id) {
            return this._rpc({
                model: "record.changeset.change",
                method: "apply",
                args: [[id]],
                context: _.extend({}, this.context, {set_change_by_ui: true}),
            });
        },

        rejectChange: function(id) {
            return this._rpc({
                model: "record.changeset.change",
                method: "cancel",
                args: [[id]],
                context: _.extend({}, this.context, {set_change_by_ui: true}),
            });
        },

        getChangeset: function(modelName, resId) {
            var self = this;
            return new Promise(function(resolve) {
                return self
                    ._rpc({
                        model: "record.changeset.change",
                        method: "get_fields_changeset_changes",
                        args: [modelName, resId],
                    })
                    .then(function(changeset) {
                        var res = {};
                        _.each(changeset, function(changesetChange) {
                            if (!_.contains(_.keys(res), changesetChange.field_name)) {
                                res[changesetChange.field_name] = [];
                            }
                            res[changesetChange.field_name].push(changesetChange);
                        });
                        resolve(res);
                    });
            });
        },
    });
});
