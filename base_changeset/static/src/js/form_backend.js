odoo.define("base_changeset.form_backend", function (require) {
    "use strict";

    var FormRenderer = require("web.FormRenderer");
    var FormController = require("web.FormController");
    var core = require("web.core");
    var qweb = core.qweb;

    FormController.include({
        start: function () {
            return this._super
                .apply(this, arguments)
                .then(this._updateChangeset(this), this._updateChangesetOne2many(this));
        },
        update: function () {
            var self = this;
            var res = this._super.apply(this, arguments);
            res.then(function () {
                self._updateChangeset();
                self._updateChangesetOne2many();
            });
            return res;
        },
        _updateChangeset: function () {
            var self = this;
            var state = this.model.get(this.handle);
            this.model
                .getChangeset(state.model, [state.data.id])
                .then(function (changeset) {
                    self.renderer.renderChangesetPopovers(changeset);
                });
        },
        _updateChangesetOne2many: function () {
            var self = this;
            var state = this.model.get(this.handle);
            this.model
                .getChangesetsOne2many(state.model, [state.data.id])
                .then(function (changesets) {
                    self.renderer.renderChangesetsOne2manyPopovers(changesets);
                });
        },
        applyChange: function (id) {
            this.model.applyChange(id).then(this.reload.bind(this));
        },
        rejectChange: function (id) {
            this.model.rejectChange(id).then(this.reload.bind(this));
        },
    });
    FormRenderer.include({
        events: {
            "click .open-changeset-create": "_actionOpenChangesetCreate",
        },
        _actionOpenChangesetCreate: function (event) {
            var self = this;
            const changeset_id = parseInt(event.currentTarget.dataset.id);
            this._rpc({
                model: "record.changeset",
                method: "get_formview_action",
                args: [[changeset_id]],
                context: {edit: false},
            }).then(function (action) {
                action.target = "new";
                action.flags = {mode: "readonly"};
                self.trigger_up("do_action", {action: action});
            });
        },
        renderChangesetPopovers: function (changeset) {
            var self = this;
            _.each(changeset, function (changes, fieldName) {
                var labelId = self._getIDForLabel(fieldName);
                var $label = self.$el.find(_.str.sprintf('label[for="%s"]', labelId));
                if (!$label.length) {
                    var widgets = _.filter(
                        self.allFieldWidgets[self.state.id],
                        function (widget) {
                            return widget.name === fieldName;
                        }
                    );
                    if (widgets.length === 1) {
                        var widget = widgets[0];
                        $label = widget.$el;
                    } else {
                        return;
                    }
                }
                self._renderChangesetPopover($label, changes);
            });
        },
        renderChangesetsOne2manyPopovers: function (changesets) {
            var self = this;
            _.each(changesets, function (changeset) {
                var fieldName = Object.keys(changeset.raw_changes)[0];
                var labelId = self._getIDForLabel(fieldName);
                var $label = $("div[id='" + labelId + "']");
                if ($label.length) {
                    var fieldNameData = self.state.data[fieldName].data;
                    if (changeset.action === "create") {
                        var $tr = $(
                            qweb.render("ChangesetRecordCreate", {
                                colspan: $label.find("thead th").length,
                                changeset_id: changeset.id,
                            })
                        );
                        if (fieldNameData.length) {
                            var last_field_name_id = fieldNameData.slice(-1)[0].id;
                            var $labelLastTr = $label.find(
                                "tr[data-id='" + last_field_name_id + "']"
                            );
                        } else {
                            var $labelLastTr = $label.find("tr").eq(0);
                        }
                        $labelLastTr.closest("tr").after($tr);
                    } else if (changeset.action === "unlink") {
                        fieldNameData.forEach(function (line) {
                            if (line.res_id === changeset.res_id) {
                                $label
                                    .find("tr[data-id='" + line.id + "']")
                                    .addClass("changeset-unlink");
                            }
                        });
                    }
                }
            });
        },
    });
});
