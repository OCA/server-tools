/** @odoo-module **/

import {CustomFilterItem} from "@web/search/filter_menu/custom_filter_item";
import {patch} from "@web/core/utils/patch";

patch(CustomFilterItem.prototype, "float_nullable_search", {
    setup() {
        this._super.apply(this, arguments);
        // Add the field type float_nullable to recognized types
        this.FIELD_TYPES.float_nullable = "number";
    },

    validateField(field) {
        return (
            this._super(field) ||
            (field.type === "float_nullable" && field.searchable && !field.deprecated)
        );
    },
});
