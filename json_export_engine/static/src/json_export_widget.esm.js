/** @odoo-module */

/* Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
 @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
 License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Many2OneField, many2OneField} from "@web/views/fields/many2one/many2one_field";
import {rpc} from "@web/core/network/rpc";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {ExportDataDialog} from "@web/views/view_dialogs/export_data_dialog";

class JsonExportDialog extends ExportDataDialog {
    setup() {
        const exporter_id =
            this.props.root.data.exporter_id && this.props.root.data.exporter_id[0];
        super.setup();
        Object.assign(this.state, {
            showApplyTemplateButton: false,
        });
        // Set templateId BEFORE parent's onWillStart runs
        if (exporter_id) {
            this.state.templateId = exporter_id;
        } else {
            this.state.templateId = "new_template";
        }
    }

    async loadExportList(value) {
        this.state.templateId = value === "new_template" ? value : Number(value);
        this.state.isEditingTemplate = value === "new_template";
        if (!value || value === "new_template") {
            this.state.exportList = [];
            return;
        }
        // Read ir.exports.line records directly instead of using RPC
        // This avoids backend assumptions about "name" field
        try {
            const exportRecord = await this.orm.read(
                "ir.exports",
                [Number(value)],
                ["export_fields"]
            );
            if (
                exportRecord.length &&
                exportRecord[0].export_fields &&
                exportRecord[0].export_fields.length
            ) {
                const lineRecords = await this.orm.read(
                    "ir.exports.line",
                    exportRecord[0].export_fields,
                    ["name"]
                );

                // Convert to format expected by exportList (with id property)
                this.state.exportList = lineRecords.map((line) => ({
                    id: line.name,
                    string: line.name,
                }));
            } else {
                this.state.exportList = [];
            }
        } catch {
            this.state.exportList = [];
        }
    }

    async onChangeExportList(ev) {
        this.state.templateId = ev.target.value;
        await this.loadExportList(ev.target.value);
        // Show "Apply" button when user selects a different saved template
        const currentId =
            this.props.root.data.exporter_id && this.props.root.data.exporter_id[0];
        if (
            this.state.templateId === currentId ||
            this.state.templateId === "new_template"
        ) {
            this.state.showApplyTemplateButton = false;
        } else {
            this.state.showApplyTemplateButton = true;
        }
    }

    onClickApplyTemplateButton() {
        const arrayOfTemplates = this.templates.map(({id, name}) => [id, name]);
        const templ = arrayOfTemplates.find(
            (subArray) => subArray[0] === this.state.templateId
        );
        if (templ) {
            this.props.context.overlap(templ);
        }
        this.props.close();
    }

    async onUpdateExportTemplate() {
        const fieldCommands = [];
        // [5] clears all existing export_fields records - simpler and more robust
        fieldCommands.push([5]);
        // Create new lines for all selected fields
        for (const field of this.state.exportList) {
            fieldCommands.push([0, 0, {name: field.id}]);
        }
        await this.orm.write("ir.exports", [this.state.templateId], {
            export_fields: fieldCommands,
        });
        this.state.isEditingTemplate = false;
    }
}
JsonExportDialog.template = "json_export_engine.JsonExportDialog";

class JsonExportFieldSelector extends Many2OneField {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.quickOverlap = (templ) => {
            if (templ && templ[0] && templ[1]) {
                return this.props.update(templ);
            }
        };
    }

    async downloadExport() {
        // No-op: we use the dialog for field selection, not actual export
        return true;
    }

    async getExportedFields(model, import_compat, parentParams) {
        const domain = [];
        return await rpc("/web/export/get_fields", {
            ...parentParams,
            model: this.props.record.data.model_name,
            domain,
            import_compat,
        });
    }

    openFieldSelector() {
        const modelName = this.props.record.data.model_name;
        if (!modelName) {
            // Model not selected yet - cannot open field selector
            return;
        }
        const exporter_id = this.props.record.data.exporter_id
            ? this.props.record.data.exporter_id[0]
            : false;
        const dialogProps = {
            context: {
                ...this.props.record.context,
                resModel: modelName,
                exporter_id: exporter_id,
                overlap: (templ) => {
                    this.quickOverlap(templ);
                },
            },
            defaultExportList: [],
            download: this.downloadExport.bind(this),
            getExportedFields: this.getExportedFields.bind(this),
            root: this.props.record.model.root,
        };
        this.dialogService.add(JsonExportDialog, dialogProps);
    }
}

JsonExportFieldSelector.template = "json_export_engine.JsonExportFieldSelector";
JsonExportFieldSelector.supportedTypes = ["many2one"];

export const jsonExportFieldSelector = {
    ...many2OneField,
    component: JsonExportFieldSelector,
};

registry.category("fields").add("json_export_field_selector", jsonExportFieldSelector);
