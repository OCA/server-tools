odoo.define("base_changeset.list_backend", function (require) {
    "use strict";

    var ListRenderer = require("web.ListRenderer");

    ListRenderer.include({
        /* eslint-disable no-unused-vars */
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.lastChangeset = false;
        },
        _onToggleOptionalColumnDropdown: function (ev) {
            this._super.apply(this, arguments);
            // HACK to trigger the renderChangesetPopovers when user has added / removed an optional column
            if (!$(ev.target).hasClass("o_optional_columns_dropdown_toggle")) {
                this.renderChangesetPopovers(this.lastChangeset);
            }
        },
        renderChangesetPopovers: function (changeset) {
            var self = this;
            this.lastChangeset = changeset;
            // Split changes by record id first
            var changesetById = {};
            _.each(changeset, function (changes, fieldName) {
                _.each(changes, function (change) {
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
            _.each(Object.values(changesetById), function (changesById) {
                _.each(changesById, function (changes, fieldName) {
                    var resId = parseInt(changes[0].record_id.split(",")[1]);
                    var dataId = self.state.data.filter(function (element) {
                        return element.res_id === resId;
                    });
                    if (dataId.length > 0) {
                        var bodyRow = self.$el.find("[data-id='" + dataId[0].id + "']");
                        var $tr = self.$(".o_list_table").find("thead").find("tr");
                        var i = 0;
                        var cellPos = 0;
                        _.each($tr.children(), function (td) {
                            if ($(td).data("name") === fieldName) {
                                cellPos = i;
                            }
                            i += 1;
                        });
                        if (cellPos !== 0) {
                            self._renderChangesetPopover(
                                $(bodyRow.children().get(cellPos)),
                                changes
                            );
                        }
                    }
                });
            });
        },
    });
});
