/** @odoo-module **/

import {Component} from "@odoo/owl";
import {Field} from "@web/views/fields/field";
import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import {listView} from "@web/views/list/list_view";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";

const fields = registry.category("fields");

class CustomInfoField extends Field {
    get fieldComponentProps() {
        // These embedded values follow the parent form's edit mode.
        const {list, ...props} = super.fieldComponentProps;
        const {record, name} = this.props;
        return {
            ...props,
            readonly: this.props.readonly,
            update: async (value) => {
                await record.update({[name]: value});
                // 16.0 only propagates inline changes automatically for list mode.
                await record.model.updateRecord(list, record);
            },
        };
    }
}

class CustomInfoRenderer extends Component {
    getFieldProps(record) {
        const name = `value_${record.data.field_type}`;
        const fieldInfo = this.props.archInfo.fieldNodes[name];
        if (!fieldInfo) {
            return null;
        }
        return {
            name,
            record,
            list: this.props.list,
            id: `custom_info_${record.id}_${name}`,
            attrs: fieldInfo.rawAttrs,
            readonly: this.props.readonly,
            fieldInfo: {
                ...fieldInfo,
                FieldComponent: fields.get(
                    record.data.widget,
                    fieldInfo.FieldComponent
                ),
            },
        };
    }
}

CustomInfoRenderer.template = "base_custom_info.table";
CustomInfoRenderer.components = {CustomInfoField};
CustomInfoRenderer.props = {archInfo: Object, list: Object, readonly: Boolean};

registry.category("views").add("custom_info", {...listView, type: "custom_info"});

patch(X2ManyField.prototype, "base_custom_info.x2many", {
    get rendererProps() {
        if (this.viewMode === "custom_info") {
            return {
                archInfo: this.activeField.views.custom_info,
                list: this.list,
                readonly: this.props.readonly,
            };
        }
        return this._super();
    },
});

X2ManyField.components = {...X2ManyField.components, CustomInfoRenderer};
