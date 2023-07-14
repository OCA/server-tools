odoo.define("base_generic_import.ImportMenu", function (require) {
    "use strict";

    const core = require("web.core");
    const DropdownMenuItem = require("web.DropdownMenuItem");
    const FavoriteMenu = require("web.FavoriteMenu");
    const {useModel} = require("web/static/src/js/model.js");

    const _t = core._t;

    /**
     * Import Records menu
     *
     * This component is used to import the records for particular model.
     *
     * @extends DropdownMenuItem
     */
    class GenImportMenu extends DropdownMenuItem {
        constructor() {
            super(...arguments);
            this.model = useModel("searchModel");
        }

        /**
         * @private
         */
        _onImportClick() {
            const action = {
                type: "ir.actions.act_window",
                name: _t("Import Processor"),
                target: "new",
                view_mode: "form",
                res_model: "import.processor.wizard",
                views: [[false, "form"]],
                context: {
                    default_model: this.model.config.modelName,
                },
            };
            this.trigger("do-action", {action: action});
        }

        /**
         * @param {Object} env
         * @returns {Boolean}
         */
        static shouldBeDisplayed(env) {
            return (
                env.view &&
                ["kanban", "list"].includes(env.view.type) &&
                !env.device.isMobile &&
                Boolean(JSON.parse(env.view.arch.attrs.import || "1")) &&
                Boolean(JSON.parse(env.view.arch.attrs.create || "1"))
            );
        }
    }

    GenImportMenu.props = {};
    GenImportMenu.template = "import_processor.ProcessorMenu";

    FavoriteMenu.registry.add("importer", GenImportMenu, 1);

    return GenImportMenu;
});
