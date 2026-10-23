import {Component} from "@odoo/owl";
import {DropdownItem} from "@web/core/dropdown/dropdown_item";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {_t} from "@web/core/l10n/translation";

const favoriteMenuRegistry = registry.category("favoriteMenu");

/**
 * Import Records menu
 *
 * This component is used to import the records for particular model.
 *
 * @extends Component
 */
export class GenImportMenu extends Component {
    static template = "import_processor.ProcessorMenu";
    static components = {DropdownItem};

    setup() {
        this.action = useService("action");
    }

    /**
     * @private
     */
    _onImportClick() {
        const {resModel} = this.env.searchModel;
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

export const importerItem = {
    Component: GenImportMenu,
    groupNumber: 4,
    isDisplayed: (env) => {
        const {config, isSmall} = env;
        return (
            !isSmall &&
            config.actionType === "ir.actions.act_window" &&
            ["kanban", "list"].includes(config.viewType) &&
            Boolean(JSON.parse(config.viewArch.getAttribute("import") || "1")) &&
            Boolean(JSON.parse(config.viewArch.getAttribute("create") || "1"))
        );
    },
};

favoriteMenuRegistry.add("importer", importerItem, {sequence: 1});
