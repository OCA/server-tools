/* @odoo-module */

import {XMLParser} from "@web/core/utils/xml";
import {_t} from "@web/core/l10n/translation";
import {Field} from "@web/views/fields/field";

export class CustomInfoArchParser extends XMLParser {
    parse(arch, models, modelName) {
        const archInfo = {
            fieldNames: [],
            __rawArch: arch,
            fieldNodes: {},
            activeFields: {},
        };

        this.visitXML(arch, (node) => {
            switch (node.tagName) {
                case "field":
                    this.visitField(node, archInfo, models, modelName);
                    break;
            }
        });
        return archInfo;
    }
    visitField(node, archInfo, models, modelName) {
        archInfo.fieldNames.push(node.getAttribute("name"));
        const fieldInfo = Field.parseFieldNode(node, models, modelName);
        const name = fieldInfo.name;
        archInfo.fieldNodes[name] = fieldInfo;
        for (const [key, field] of Object.entries(archInfo.fieldNodes)) {
            archInfo.activeFields[key] = field;
        }
    }
}
