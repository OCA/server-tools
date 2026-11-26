import {Field, getFieldFromRegistry} from "@web/views/fields/field";
import {Component} from "@odoo/owl";
import {ListArchParser} from "@web/views/list/list_arch_parser";
import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import {evaluateBooleanExpr} from "@web/core/py_js/py";
import {listView} from "@web/views/list/list_view";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";

class CustomInfoArchParser extends ListArchParser {
    parse(xmlDoc, models, modelName) {
        // The standard parser initializes list options only for a <list> root.
        const list = xmlDoc.ownerDocument.createElement("list");
        for (const {name, value} of xmlDoc.attributes) {
            list.setAttribute(name, value);
        }
        list.append(...Array.from(xmlDoc.childNodes, (node) => node.cloneNode(true)));
        return super.parse(list, models, modelName);
    }
}

class CustomInfoField extends Field {
    get fieldComponentProps() {
        const {fieldInfo, record, readonly} = this.props;
        // Rows in this subview follow the parent form's edit mode.
        return {
            ...super.fieldComponentProps,
            readonly:
                readonly ||
                evaluateBooleanExpr(
                    fieldInfo.readonly,
                    record.evalContextWithVirtualIds
                ),
        };
    }
}

class CustomInfoRenderer extends Component {
    static template = "base_custom_info.table";
    static components = {CustomInfoField};
    static props = {archInfo: Object, list: Object, readonly: Boolean};

    getFieldProps(record) {
        const name = `value_${record.data.field_type}`;
        const fieldInfo = Object.values(this.props.archInfo.fieldNodes).find(
            (node) => node.name === name
        );
        if (!fieldInfo) {
            return null;
        }
        return {
            name,
            record,
            id: `custom_info_${record.id}_${name}`,
            readonly: this.props.readonly,
            fieldInfo: {
                ...fieldInfo,
                field: getFieldFromRegistry(fieldInfo.type, record.data.widget),
            },
        };
    }
}

registry.category("views").add("custom_info", {
    ...listView,
    type: "custom_info",
    ArchParser: CustomInfoArchParser,
});

patch(X2ManyField.prototype, {
    get rendererProps() {
        if (this.props.viewMode === "custom_info") {
            return {
                archInfo: this.archInfo,
                list: this.list,
                readonly: this.props.readonly,
            };
        }
        return super.rendererProps;
    },
});

X2ManyField.components = {...X2ManyField.components, CustomInfoRenderer};
