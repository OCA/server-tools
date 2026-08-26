/** @odoo-module **/

import {FloatField} from "@web/views/fields/float/float_field";
import {_lt} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

export class FloatNullableField extends FloatField {
    parse(value) {
        if (value === "" || value === null) {
            return null;
        }
        return super.parse(value);
    }

    get formattedValue() {
        if (this.props.value === null || this.props.value === false) {
            return "";
        }
        return super.formattedValue;
    }
}

FloatNullableField.template = "field_float_nullable.FloatNullable";

FloatNullableField.displayName = _lt("Float (Nullable)");
FloatNullableField.supportedTypes = ["float_nullable", "float"];

registry.category("fields").add("float_nullable", FloatNullableField);
