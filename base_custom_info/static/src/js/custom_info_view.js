odoo.define("base_custom_info.CustomInfoView", function(require) {
    "use strict";

    var BasicView = require("web.BasicView");
    var CustomInfoRenderer = require("base_custom_info.CustomInfoRenderer");
    var view_registry = require("web.view_registry");
    var core = require("web.core");

    var _lt = core._lt;

    var CustomInfoView = BasicView.extend({
        display_name: _lt("Custom Info"),
        viewType: "custom_info",
        config: _.extend({}, BasicView.prototype.config, {
            Renderer: CustomInfoRenderer,
        }),
        multi_record: true,
        searchable: false,
    });

    view_registry.add("custom_info", CustomInfoView);

    return CustomInfoView;
});
