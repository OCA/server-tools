/** @odoo-module **/

import {registry} from "@web/core/registry";
import {CustomInfoRenderer} from "./custom_info_renderer";
import {Model} from "@web/views/model";
import {CustomInfoArchParser} from "./custom_info_arch_parser";
import {_lt} from "@web/core/l10n/translation";

export const CustomInfoView = {
    type: "custom_info",
    display_name: _lt("Custom Info"),
    multiRecord: true,
    searchMenuTypes: [],
    Renderer: CustomInfoRenderer,
    ArchParser: CustomInfoArchParser,
    Model: Model,

    props: (genericProps, view, config) => {
        let modelParams = genericProps.state;
        if (!modelParams) {
            const {context} = genericProps;
            modelParams = {
                context: context,
            };
        }

        return {
            ...genericProps,
            Model: view.Model,
            modelParams,
            Renderer: view.Renderer,
        };
    },
};

registry.category("views").add("custom_info", CustomInfoView);

// odoo.define("base_custom_info.CustomInfoView", function (require) {
//     "use strict";

//     var BasicView = require("web.BasicView");
//     var CustomInfoRenderer = require("base_custom_info.CustomInfoRenderer");
//     var view_registry = require("web.view_registry");
//     var core = require("web.core");

//     var _lt = core._lt;

//     var CustomInfoView = BasicView.extend({
//         display_name: _lt("Custom Info"),
//         viewType: "custom_info",
//         config: _.extend({}, BasicView.prototype.config, {
//             Renderer: CustomInfoRenderer,
//         }),
//         multi_record: true,
//         searchable: false,
//     });

//     view_registry.add("custom_info", CustomInfoView);

//     return CustomInfoView;
// });
