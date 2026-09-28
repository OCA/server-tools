/** @odoo-module **/

/** Copyright 2026 Kobros-Tech Ltd (http://kobros-tech.com).
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
 */

import {Component, useState} from "@odoo/owl";

export class RuleExplainer extends Component {
    setup() {
        this.state = useState({
            step1: false,
            step2: false,
            step3: true,
        });
    }

    toggleStep(step) {
        this.state[step] = !this.state[step];
    }

    formatDomain(domain) {
        if (typeof domain === "string") {
            return domain;
        }
        return JSON.stringify(domain, null, 2);
    }

    get context() {
        return this.props.analysisResult.context || {};
    }

    get crudSummary() {
        return this.props.analysisResult.crud_summary || {};
    }

    get summaryTable() {
        return this.crudSummary.summary_table || [];
    }

    get recordRulesPerOp() {
        return this.props.analysisResult.record_rules_per_op || {};
    }

    get simulations() {
        return this.props.analysisResult.simulations || null;
    }

    get hasConflicts() {
        return this.crudSummary.conflicts_detected || false;
    }

    get operations() {
        return ["create", "read", "write", "unlink"];
    }

    get operationLabels() {
        return {create: "Create", read: "Read", write: "Write", unlink: "Delete"};
    }

    get operationShortLabels() {
        return {create: "C", read: "R", write: "W", unlink: "D"};
    }

    /**
     * Quick verdict badges for Step 1 header (shown when collapsed)
     */
    get step1Badges() {
        return this.summaryTable.map((row) => ({
            label: row.operation.charAt(0),
            allowed: row.allowed,
        }));
    }

    /**
     * Count total unique record rules across all operations
     */
    get totalRecordRules() {
        const seen = new Set();
        for (const op of this.operations) {
            const opRules = this.recordRulesPerOp[op];
            if (opRules && opRules.rules) {
                for (const rule of opRules.rules) {
                    seen.add(rule.id);
                }
            }
        }
        return seen.size;
    }

    /**
     * Get record rules that apply to a specific operation
     */
    getRulesForOp(op) {
        return this.recordRulesPerOp[op] || {};
    }

    hasRulesForOp(op) {
        const opRules = this.recordRulesPerOp[op];
        return opRules && opRules.rules && opRules.rules.length > 0;
    }
}

RuleExplainer.template = "security_visualizer.RuleExplainer";
RuleExplainer.props = {
    analysisResult: {type: Object},
};
