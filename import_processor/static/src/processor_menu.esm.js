/** @odoo-module **/

import core from 'web.core';
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component } = owl;
const favoriteMenuRegistry = registry.category("favoriteMenu");

const _t = core._t;

/**
 * Import Records menu
 *
 * This component is used to import the records for particular model.
 *
 * @extends Component
 */
export class GenImportMenu extends Component {
    setup() {
        this.action = useService("action");
    }

    /**
     * @private
     */
    _onImportClick() {
        const { context, resModel } = this.env.searchModel;
        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Import Processor"),
            target: "new",
            view_mode: "form",
            res_model: "import.processor.wizard",
            views: [[false, "form"]],
            context: {
                default_model: resModel,
            },
        });
    }
}

GenImportMenu.template = "import_processor.ProcessorMenu";
GenImportMenu.components = { DropdownItem };

export const importerItem = {
    Component: GenImportMenu,
    groupNumber: 4,
    isDisplayed: ({ config, isSmall }) =>
        !isSmall &&
        config.actionType === "ir.actions.act_window" &&
        ["kanban", "list"].includes(config.viewType) &&
        !!JSON.parse(config.viewArch.getAttribute("import") || "1") &&
        !!JSON.parse(config.viewArch.getAttribute("create") || "1"),
};

favoriteMenuRegistry.add("importer", importerItem, { sequence: 1 });
