/** @odoo-module **/

/** Copyright 2026 Kobros-Tech Ltd (http://kobros-tech.com).
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
 */

import {Component} from "@odoo/owl";

export class AccessMatrix extends Component {
    get operationLabels() {
        return {create: "C", read: "R", write: "W", unlink: "D"};
    }

    get operations() {
        return ["create", "read", "write", "unlink"];
    }

    /**
     * Get cell data for user, model, operation combination
     */
    getCellData(userId, modelId, operation) {
        const key = `${userId},${modelId},${operation}`;
        return this.props.matrixData.cells[key] || {has_access: false, rule_count: 0};
    }

    getCellClass(hasAccess) {
        return hasAccess ? "access-allowed" : "access-denied";
    }
}

AccessMatrix.template = "security_visualizer.AccessMatrix";
AccessMatrix.props = {
    matrixData: {type: Object},
};
