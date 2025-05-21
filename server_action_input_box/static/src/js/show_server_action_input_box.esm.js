/* global document */

//  Copyright 2024 jesanmor - Jesús Sánchez <jesanmor.dev@gmail.com>
//  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import {Component, onMounted} from "@odoo/owl";
import {ConfirmationDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class ShowServerActionInputBox extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.params = this.props.action.params;
        this.lineIds = this.params.line_ids;
        this.id = this.params.id;
        this.records_ids = this.params.records_ids;
        this.binding_model = this.params.binding_model;
        this.show_confirmation_dialog = this.params.show_confirmation_dialog;
        this.parameters_dict = {};
        this.singleEditionCheckboxState = false;
        this.context = this.params.context;

        onMounted(() => {
            // Removes the accept button that the action adds by default
            const acceptButton = document.querySelector(
                "footer button.o-default-button"
            );
            if (acceptButton) {
                acceptButton.remove();
            }

            this.load_data();
            this._setHeaderRecordName(this.records_ids);
        });
    }

    async load_data() {
        const records = await this.orm.searchRead(
            "server.action.input.box.line",
            [["id", "in", this.lineIds]],
            ["parameter_label", "id", "name", "data_type"]
        );

        const container = document.querySelector(".o_show_server_action_input_box");

        records.forEach((record) => {
            const label = document.createElement("h5");
            label.textContent = record.parameter_label;
            container.append(label);

            if (record.data_type === "bool") {
                const checkboxField = document.createElement("input");
                checkboxField.type = "checkbox";
                checkboxField.classList.add("o_checkbox");
                container.append(checkboxField);
                this.parameters_dict[record.name] = false;

                checkboxField.addEventListener("change", () => {
                    this.parameters_dict[record.name] = checkboxField.checked;
                });
            } else {
                const inputField = document.createElement("input");
                inputField.type = "text";
                inputField.classList.add("o_input");
                inputField.style.marginBottom = "15px";
                container.append(inputField);
                this.parameters_dict[record.name] = "";

                inputField.addEventListener("blur", () => {
                    this.parameters_dict[record.name] = inputField.value;
                });
            }
        });

        const checkbox = document.querySelector(".single-edition-checkbox .o_input");
        checkbox.addEventListener("change", () => {
            this.singleEditionCheckboxState = checkbox.checked;
            this._setHeaderRecordName(this.records_ids);
        });
    }

    _nextSingleEdition() {
        this.records_ids = this.records_ids.slice(1);
        if (this.records_ids.length === 0) {
            this.action.doAction({type: "ir.actions.act_window_close"});
        }
    }

    async _setHeaderRecordName(record_id) {
        const serverRecordNameElement = document.querySelector(".server-record-name");
        if (record_id.length > 0) {
            if (this.singleEditionCheckboxState) {
                const records = await this.orm.searchRead(
                    this.binding_model,
                    [["id", "=", record_id[0]]],
                    // Leave empty to import all fields
                    ["display_name"]
                );
                serverRecordNameElement.textContent =
                    _t("Modifying record: ") + records[0].display_name;
            } else {
                serverRecordNameElement.textContent =
                    _t("Modifying: ") + record_id.length + _t(" records");
            }
        }
    }

    async _executeActionAndClose() {
        if (this.singleEditionCheckboxState) {
            await this.orm.call("server.action.input.box", "do_action", [
                this.id,
                this.binding_model,
                [this.records_ids[0]],
                this.parameters_dict,
                this.context,
            ]);
            this._nextSingleEdition();
        } else {
            const result = await this.orm.call("server.action.input.box", "do_action", [
                this.id,
                this.binding_model,
                this.records_ids,
                this.parameters_dict,
                this.context,
            ]);
            this.action.doAction({type: "ir.actions.act_window_close"});
            if (result.type || typeof result === "number") {
                // This code is to include the view modes specified
                // in view_mode in views in case views are empty.
                // This is done to avoid an error if views are empty.
                if (result.type === "ir.actions.act_window") {
                    if (!result.views) {
                        // If views is empty we extract the views to a list
                        const view_mode = result.view_mode.split(",");
                        // From the list above we include the views in false mode
                        result.views = view_mode.map((view) => [false, view]);
                    }
                }

                this.action.doAction(result);
            }
        }
        this._setHeaderRecordName(this.records_ids);
    }

    _onAcceptButtonClick() {
        if (this.show_confirmation_dialog) {
            this.dialog.add(ConfirmationDialog, {
                title: _t("Write Confirmation"),
                body: _t("You are going to modify records"),
                confirm: () => {
                    this._executeActionAndClose();
                },
            });
        } else {
            this._executeActionAndClose();
        }
    }

    _onCancelButtonClick() {
        this.action.doAction({type: "ir.actions.act_window_close"});
    }
}

ShowServerActionInputBox.template = "ShowServerActionInputBoxTemplate";
ShowServerActionInputBox.props = {
    action: Object,
    actionId: {type: Number, optional: true, default: undefined},
    updateActionState: {type: Function},
};

registry
    .category("actions")
    .add("show_server_action_input_box", ShowServerActionInputBox);
