odoo.define("base_changeset.list_backend", function(require) {
    "use strict";

    var ListRenderer = require("web.ListRenderer");
    var ListController = require("web.ListController");
    var core = require("web.core");
    var qweb = core.qweb;

    ListController.include({
        start: function() {
            return this._super
                .apply(this, arguments)
                .then(this._updateChangeset.bind(this));
        },

        update: function() {
            var self = this;
            var res = this._super.apply(this, arguments);
            res.then(function() {
                self._updateChangeset();
            });
            return res;
        },

        _updateChangeset: function() {
            var self = this;
            var state = this.model.get(this.handle);
            this.model.getChangeset(state.model, false).then(function(changeset) {
                self.renderer.renderChangesetPopovers(changeset);
            });
        },

        applyChange: function(id) {
            this.model.applyChange(id).then(this.reload.bind(this));
        },

        rejectChange: function(id) {
            this.model.rejectChange(id).then(this.reload.bind(this));
        },
    });

    ListRenderer.include({
        /* eslint-disable no-unused-vars */
        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.lastChangeset = false;
        },

        _onToggleOptionalColumnDropdown: function(ev) {
            this._super.apply(this, arguments);
            // HACK to trigger the renderChangesetPopovers when user has added / removed an optional column
            if (!$(ev.target).hasClass("o_optional_columns_dropdown_toggle")) {
                this.renderChangesetPopovers(this.lastChangeset);
            }
        },

        renderChangesetPopovers: function(changeset) {
            var self = this;
            this.lastChangeset = changeset;
            // Split changes by record id first
            var changesetById = {};
            _.each(changeset, function(changes, fieldName) {
                _.each(changes, function(change) {
                    var resId = change.record_id;
                    if (resId in changesetById) {
                        if (fieldName in changesetById[resId]) {
                            changesetById[resId][fieldName].push(change);
                        } else {
                            changesetById[resId][fieldName] = [change];
                        }
                    } else {
                        changesetById[resId] = {};
                        changesetById[resId][fieldName] = [change];
                    }
                });
            });
            // Render the popover in the correct row / column position
            _.each(Object.values(changesetById), function(changesById) {
                _.each(changesById, function(changes, fieldName) {
                    var resId = changes[0].record_id.split(",")[1];
                    var dataId = self.state.data.filter(function(element) {
                        return element.res_id == resId;
                    });
                    if (dataId.length > 0) {
                        var bodyRow = self.$el.find("[data-id='" + dataId[0].id + "']");
                        var $tr = self.$el.find("thead").find("tr");
                        var i = 0;
                        var cellPos = 0;
                        _.each($tr.children(), function(td) {
                            if ($(td).data("name") == fieldName) {
                                cellPos = i;
                            }
                            i += 1;
                        });
                        if (cellPos != 0) {
                            self._renderChangesetPopover(
                                $(bodyRow.children().get(cellPos)),
                                changes
                            );
                        }
                    }
                });
            });
        },

        _renderChangesetPopover: function($el, changes) {
            var self = this;
            if (this.mode !== "readonly") {
                return;
            }
            var $button = $(
                qweb.render("ChangesetButton", {
                    count: changes.length,
                })
            );

            $button.on("click", function(ev) {
                ev.stopPropagation();
            });

            $el.prepend($button);

            var options = {
                content: function() {
                    var $content = $(
                        qweb.render("ChangesetPopover", {
                            changes: changes,
                        })
                    );
                    $content.find(".base_changeset_apply").on("click", function() {
                        self._applyClicked($(this));
                    });
                    $content.find(".base_changeset_reject").on("click", function() {
                        self._rejectClicked($(this));
                    });
                    return $content;
                },
                html: true,
                placement: "bottom",
                title: "Pending Changes",
                trigger: "focus",
                delay: {show: 0, hide: 100},
                template: qweb.render("ChangesetTemplate"),
            };

            $button.popover(options);
        },

        _applyClicked: function($el) {
            var id = parseInt($el.data("id"), 10);
            this.getParent().applyChange(id);
        },

        _rejectClicked: function($el) {
            var id = parseInt($el.data("id"), 10);
            this.getParent().rejectChange(id);
        },
    });
});
