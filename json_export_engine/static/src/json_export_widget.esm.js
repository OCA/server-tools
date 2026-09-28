/** @odoo-module **/

/* Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
 @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
 License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {ExportDataDialog} from "@web/views/view_dialogs/export_data_dialog";
import {Many2OneField} from "@web/views/fields/many2one/many2one_field";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const {onWillDestroy} = owl;

class JsonExportDialog extends ExportDataDialog {
    setup() {
        super.setup();
        Object.assign(this.state, {
            showApplyTemplateButton: false,
        });
        this.title = this.env._t("Select Fields for JSON Export");
        // Swap the model from props to load the correct export fields
        // for the schema's target model, not the schema model itself.
        this.swapResModel = this.props.root.resModel;
        this.props.root.resModel = this.props.context.resModel;
        if (this.props.context.exporter_id && this.props.context.exporter_id[0]) {
            this.state.templateId = this.props.context.exporter_id[0];
        } else {
            this.state.templateId = "new_template";
        }
        // Restore original model when dialog is destroyed
        onWillDestroy(() => {
            this.props.root.resModel = this.swapResModel;
        });
    }

    async onChangeExportList(ev) {
        this.loadExportList(ev.target.value);
        // Show "Apply" button when user selects a different saved template
        const currentId =
            this.props.context.exporter_id && this.props.context.exporter_id[0];
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
        const oldRec = await this.orm.read(
            "ir.exports",
            [this.state.templateId],
            ["name", "export_fields"]
        );
        let oldLines = [];
        if (
            oldRec.length &&
            oldRec[0].export_fields &&
            oldRec[0].export_fields.length
        ) {
            oldLines = await this.orm.read("ir.exports.line", oldRec[0].export_fields, [
                "name",
            ]);
        }
        const newFieldNames = this.state.exportList.map((field) => field.id);
        const oldFieldMap = Object.fromEntries(
            oldLines.map((line) => [line.name, line.id])
        );
        const fieldCommands = [];
        // Keep existing or create new lines
        for (const field of this.state.exportList) {
            if (oldFieldMap[field.id]) {
                fieldCommands.push([4, oldFieldMap[field.id]]);
            } else {
                fieldCommands.push([0, 0, {name: field.id}]);
            }
        }
        // Unlink removed fields
        for (const oldLine of oldLines) {
            if (!newFieldNames.includes(oldLine.name)) {
                fieldCommands.push([3, oldLine.id]);
            }
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
        this.rpc = useService("rpc");
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
        return await this.rpc("/web/export/get_fields", {
            ...parentParams,
            model,
            import_compat,
        });
    }

    openFieldSelector() {
        const modelName = this.props.record.data.model_name;
        if (!modelName) {
            // Model not selected yet - cannot open field selector
            return;
        }
        const dialogProps = {
            context: {
                ...this.props.record.context,
                resModel: modelName,
                exporter_id: this.props.value || false,
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
JsonExportFieldSelector.fieldDependencies = {
    model_name: {type: "char"},
};

registry.category("fields").add("json_export_field_selector", JsonExportFieldSelector);
