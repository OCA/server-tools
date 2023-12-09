/** @odoo-module **/

import {CustomInfoRenderer} from "./custom_info_renderer";
import {FieldOne2Many} from "web.relational_fields";
import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import {Field} from "@web/views/fields/field";
import {
    archParseBoolean,
    evalDomain,
    getClassNameFromDecoration,
    X2M_TYPES,
} from "@web/views/utils";
import {patch} from "web.utils";

// patch(FieldOne2Many.prototype, 'base_custom_info_field_one_2_many', {
//     _getRenderer: function () {
//         if (this.view.arch.tag === "custom_info") {
//             return CustomInfoRenderer;
//         }
//         return this._super.apply(this, arguments);
//     },
//     _updateCustomInfoItem: function (data) {
//         var result = {
//             value_float: data.value_float,
//             value_str: data.value_str,
//             value_int: data.value_int,
//             value_bool: data.value_bool,
//             value_date: data.value_date,
//         };
//         if (data.value_id.res_id !== undefined)
//             result.value_id = {id: data.value_id.res_id};
//         return result;
//     },
//     _saveCustomInfo: function () {
//         var self = this;
//         _.each(this.renderer.recordWidgets, function (widget) {
//             self._setValue({
//                 operation: "UPDATE",
//                 id: widget.dataPointID,
//                 data: self._updateCustomInfoItem(widget.recordData),
//             });
//         });
//     },
//     commitChanges: function () {
//         if (this.renderer && this.renderer.viewType === "custom_info") {
//             var self = this;
//             this.renderer.commitChanges().then(function () {
//                 return self._saveCustomInfo();
//             });
//         }
//         return this._super.apply(this, arguments);
//     },
//     activate: function () {
//         var result = this._super.apply(this, arguments);
//         if (result && this.renderer.viewType === "custom_info") {
//             if (this.renderer.recordWidgets.length > 0) {
//                 this.renderer.recordWidgets[0].$input.focus();
//             }
//         }
//         return result;
//     },
// });

patch(Field.prototype, "base_custom_info_field", {
    get fieldComponentProps() {
        const record = this.props.record;
        const evalContext = record.evalContext;
        const field = record.fields[this.props.name];
        const fieldInfo = this.props.fieldInfo;

        if (!fieldInfo.FiledType || fieldInfo.FiledType != "custom") {
            return this._super(...arguments);
        }

        const modifiers = fieldInfo.modifiers || {};
        // const readonlyFromModifiers = evalDomain(modifiers.readonly, evalContext);
        const readonlyFromModifiers = false;

        // Decoration props
        const decorationMap = {};
        const {decorations} = fieldInfo;
        for (const decoName in decorations) {
            const value = evaluateExpr(decorations[decoName], evalContext);
            decorationMap[decoName] = value;
        }

        let propsFromAttrs = fieldInfo.propsFromAttrs;
        if (this.props.attrs) {
            const extractProps = this.FieldComponent.extractProps || (() => ({}));
            propsFromAttrs = extractProps({
                field,
                attrs: {
                    ...this.props.attrs,
                    options: evaluateExpr(this.props.attrs.options || "{}"),
                },
            });
        }

        const props = {...this.props};
        delete props.style;
        delete props.class;
        delete props.showTooltip;
        delete props.fieldInfo;
        delete props.attrs;

        return {
            ...fieldInfo.props,
            update: async (value, options = {}) => {
                const {save} = Object.assign({save: false}, options);
                await record.update({[this.props.name]: value});
                if (record.selected && record.model.multiEdit) {
                    return;
                }
                const rootRecord =
                    record.model.root instanceof record.constructor &&
                    record.model.root;
                const isInEdition = rootRecord
                    ? rootRecord.isInEdition
                    : record.isInEdition;
                // if ((!isInEdition && !readonlyFromModifiers) || save) {
                //     // TODO: maybe move this in the model
                //     return record.save();
                // }
                return record.save();
            },
            value: this.props.record.data[this.props.name],
            decorations: decorationMap,
            // readonly: !record.isInEdition || readonlyFromModifiers || false,
            readonly: false,
            ...propsFromAttrs,
            ...props,
            type: field
                ? field.type
                : this.props.type || this.props.record.fields[this.props.name].type,
        };
    },
});
patch(X2ManyField.prototype, "base_custom_info_x2_many_field", {
    get rendererProps() {
        if (this.viewMode === "custom_info") {
            return {
                model: this.env.model,
                list: this.list,
            };
        }
        return this._super(...arguments);
    },
});
X2ManyField.components = {
    ...X2ManyField.components,
    CustomInfoRenderer: CustomInfoRenderer,
};
