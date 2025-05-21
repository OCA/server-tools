//  Copyright 2024 jesanmor - Jesús Sánchez <jesanmor.dev@gmail.com>
//  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

odoo.define("server_action_input_box.show_server_action_inputbox", function (require) {
    var core = require("web.core");
    var Dialog = require("web.Dialog");
    var AbstractAction = require("web.AbstractAction");
    var rpc = require("web.rpc");
    var _t = core._t;
    var ShowServerActionInputBox = AbstractAction.extend({
        template: "ShowServerActionInputBoxTemplate",
        init: function (parent, action) {
            this._super(parent, action);
            this.lineIds = action.params.line_ids;
            this.id = action.params.id;
            this.records_ids = action.params.records_ids;
            this.binding_model = action.params.binding_model;
            this.show_confirmation_dialog = action.params.show_confirmation_dialog;
            this.parameters_dict = {};
            this.singleEditionCheckboxState = false;
            this.context = action.params.context;
        },
        start: function () {
            var self = this;
            self.load_data();
            self._setHeaderRecordName(self.records_ids);
            return this._super.apply(this, arguments);
        },

        load_data: function () {
            var self = this;
            var checkbox = self.$('.single-edition-checkbox input[type="checkbox"]');
            rpc.query({
                model: "server.action.input.box.line",
                method: "read",
                args: [self.lineIds, ["parameter_label", "id", "name", "data_type"]],
            }).then(function (records) {
                records.forEach(function (record) {
                    // Incluyo label
                    var label = $("<h5>").text(record.parameter_label);
                    self.$(".o_show_server_action_input_box").append(label);

                    if (record.data_type === "bool") {
                        // I include checkbox
                        var checkboxField = $(
                            '<input type="checkbox" class="o_checkbox" />'
                        );
                        self.$(".o_show_server_action_input_box").append(checkboxField);
                        self.parameters_dict[record.name] = false;
                        // Handle the checkbox change event
                        checkboxField.on("change", function () {
                            var isChecked = checkboxField.prop("checked");
                            self.parameters_dict[record.name] = isChecked;
                        });
                    } else {
                        // I include inputField
                        var inputField = $(
                            '<input type="text" style="margin-bottom:15px" class="o_input" />'
                        );
                        self.$(".o_show_server_action_input_box").append(inputField);
                        self.parameters_dict[record.name] = "";

                        // Handle the blur event
                        inputField.on("blur", function () {
                            var inputValue = inputField.val();
                            self.parameters_dict[record.name] = inputValue;
                        });
                    }
                });
            });

            checkbox.on("change", function () {
                // Get the new state of the checkbox
                var isChecked = checkbox.prop("checked");
                self.singleEditionCheckboxState = isChecked;
                self._setHeaderRecordName(self.records_ids);
            });
        },

        _nextSingleEdition: function () {
            var self = this;
            // Remove the first element from the list, which has already been used
            self.records_ids = self.records_ids.slice(1);
            // If there are no more elements left, I close the input box
            if (self.records_ids.length === 0) {
                self.do_action({
                    type: "ir.actions.act_window_close",
                });
            }
        },

        _setHeaderRecordName: function (record_id) {
            var self = this;
            var serverRecordNameElement = self.$(".server-record-name");
            if (record_id.length > 0) {
                if (self.singleEditionCheckboxState) {
                    rpc.query({
                        model: self.binding_model,
                        method: "read",
                        args: [record_id[0]],
                    }).then(function (record) {
                        serverRecordNameElement.text(
                            _t("Modifying record: ") + record[0].display_name
                        );
                    });
                } else {
                    serverRecordNameElement.text(
                        _t("Modifying: ") + record_id.length + _t(" records")
                    );
                }
            }
        },

        _executeActionAndClose: function () {
            var self = this;
            if (self.singleEditionCheckboxState) {
                self._rpc({
                    model: "server.action.input.box",
                    method: "do_action",
                    args: [
                        self.id,
                        self.binding_model,
                        [self.records_ids[0]],
                        self.parameters_dict,
                        self.context,
                    ],
                });
                self._nextSingleEdition();
            } else {
                self._rpc({
                    model: "server.action.input.box",
                    method: "do_action",
                    args: [
                        self.id,
                        self.binding_model,
                        self.records_ids,
                        self.parameters_dict,
                        self.context,
                    ],
                }).then(function (result) {
                    self.do_action({
                        type: "ir.actions.act_window_close",
                    });
                    if (result.type || typeof result === "number") {
                        if (result.type === "ir.actions.act_window") {
                            if (!result.views) {
                                var view_mode = result.view_mode.split(",");
                                result.views = [];
                                view_mode.forEach(function (view) {
                                    result.views.push([false, view]);
                                });
                            }
                        }
                        self.do_action(result);
                    }
                });
            }
            self._setHeaderRecordName(self.records_ids);
        },

        events: {
            "click .btn-secondary": "_onCancelButtonClick",
            "click .btn-primary": "_onAcceptButtonClick",
        },

        _onAcceptButtonClick: function () {
            var self = this;
            if (self.show_confirmation_dialog) {
                Dialog.safeConfirm(self, _t("You are going to modify records"), {
                    title: _t("Write Confirmation"),
                    async confirm_callback() {
                        self._executeActionAndClose();
                    },
                });
            } else {
                self._executeActionAndClose();
            }
        },
        _onCancelButtonClick: function () {
            this.do_action({
                type: "ir.actions.act_window_close",
            });
        },
    });

    core.action_registry.add("show_server_action_input_box", ShowServerActionInputBox);
    return {
        ShowServerActionInputBox: ShowServerActionInputBox,
    };
});
