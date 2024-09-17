odoo.define("base_changeset.basic_model", function (require) {
    "use strict";

    var BasicModel = require("web.BasicModel");
    var BasicRenderer = require("web.BasicRenderer");
    var core = require("web.core");
    var qweb = core.qweb;

    BasicModel.include({
        applyChange: function (id) {
            return this._rpc({
                model: "record.changeset.change",
                method: "apply",
                args: [[id]],
                context: _.extend({}, this.context, {set_change_by_ui: true}),
            });
        },
        rejectChange: function (id) {
            return this._rpc({
                model: "record.changeset.change",
                method: "cancel",
                args: [[id]],
                context: _.extend({}, this.context, {set_change_by_ui: true}),
            });
        },

        getChangeset: function (modelName, resIds) {
            var self = this;
            return new Promise(function (resolve) {
                return self
                    ._rpc({
                        model: "record.changeset.change",
                        method: "get_fields_changeset_changes",
                        args: [modelName, resIds],
                    })
                    .then(function (changeset) {
                        var res = {};
                        _.each(changeset, function (changesetChange) {
                            if (!_.contains(_.keys(res), changesetChange.field_name)) {
                                res[changesetChange.field_name] = [];
                            }
                            res[changesetChange.field_name].push(changesetChange);
                        });
                        resolve(res);
                    });
            });
        },
        getChangesetsOne2many: function (modelName, resId) {
            var self = this;
            return new Promise(function (resolve) {
                return self
                    ._rpc({
                        model: "record.changeset",
                        method: "get_changeset_changes_one2many",
                        args: [modelName, resId],
                    })
                    .then(function (changesets) {
                        resolve(changesets);
                    });
            });
        },
    });

    BasicRenderer.include({
        /* eslint-disable no-unused-vars */
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            $(".base_changeset_popover").remove();
        },
        _renderChangesetPopover: function ($el, changes) {
            var self = this;
            if (this.mode !== "readonly") {
                return;
            }
            var $button = $(
                qweb.render("ChangesetButton", {
                    count: changes.length,
                })
            );
            $el.append($button);
            var placement_option = "bottom";
            if (self.viewType == "list") {
                var placement_option = "right";
            }
            var options = {
                content: function () {
                    var $content = $(
                        qweb.render("ChangesetPopover", {
                            changes: changes,
                        })
                    );
                    $content.find(".base_changeset_apply").on("click", function () {
                        self._applyClicked($(this));
                    });
                    $content.find(".base_changeset_reject").on("click", function () {
                        self._rejectClicked($(this));
                    });
                    return $content;
                },
                html: true,
                placement: placement_option,
                trigger: "hover focus",
                delay: {show: 0, hide: 100},
                template: qweb.render("ChangesetTemplate"),
            };
            $button.popover(options);
        },
        _applyClicked: function ($el) {
            var id = parseInt($el.data("id"), 10);
            this.getParent().applyChange(id);
        },
        _rejectClicked: function ($el) {
            var id = parseInt($el.data("id"), 10);
            this.getParent().rejectChange(id);
        },
    });
});
