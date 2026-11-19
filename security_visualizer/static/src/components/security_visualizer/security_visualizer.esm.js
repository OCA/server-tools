/** @odoo-module **/

/** Copyright 2026 Kobros-Tech Ltd (http://kobros-tech.com).
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
 */

import {
    Component,
    onMounted,
    onWillStart,
    onWillUnmount,
    useRef,
    useState,
} from "@odoo/owl";
import {AutoComplete} from "@web/core/autocomplete/autocomplete";
import {TagsList} from "@web/views/fields/many2many_tags/tags_list";
import {AccessMatrix} from "../access_matrix/access_matrix.esm";
import {RuleExplainer} from "../rule_explainer/rule_explainer.esm";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class SecurityVisualizer extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            currentView: "analyzer",

            // Analyzer single selectors
            selectedUserId: null,
            selectedUserDisplay: "",
            selectedModelDisplay: "",
            selectedModelTechnical: "",
            recordId: null,

            // Analysis results
            analysisResult: null,
            isAnalyzing: false,

            // Matrix multi selectors
            matrixUserIds: [],
            matrixUserTags: [],
            matrixModelIds: [],
            matrixModelTags: [],

            // Matrix data
            matrixData: null,
            isLoadingMatrix: false,

            // UI state
            showScrollTop: false,
        });

        onWillStart(async () => {
            const currentUser = this.env.services.user;
            this.state.selectedUserId = currentUser.userId;
            // Fetch display name for current user
            const users = await this.orm.read(
                "res.users",
                [currentUser.userId],
                ["name"]
            );
            if (users.length) {
                this.state.selectedUserDisplay = users[0].name;
            }
        });

        this.scrollRef = useRef("scrollContainer");
        this._onScroll = this.onScroll.bind(this);

        onMounted(() => {
            if (this.scrollRef.el) {
                this.scrollRef.el.addEventListener("scroll", this._onScroll);
            }
        });

        onWillUnmount(() => {
            if (this.scrollRef.el) {
                this.scrollRef.el.removeEventListener("scroll", this._onScroll);
            }
        });
    }

    onScroll() {
        const el = this.scrollRef.el;
        this.state.showScrollTop = el && el.scrollTop > 300;
    }

    scrollToTop() {
        if (this.scrollRef.el) {
            this.scrollRef.el.scrollTo({top: 0, behavior: "smooth"});
        }
    }

    // --- AutoComplete sources ---

    get userSources() {
        return [
            {
                options: async (request) => {
                    const results = await this.orm.call(
                        "res.users",
                        "name_search",
                        [],
                        {name: request, limit: 8}
                    );
                    return results.map(([id, name]) => ({
                        resId: id,
                        label: name,
                        displayName: name,
                    }));
                },
            },
        ];
    }

    get modelSources() {
        return [
            {
                options: async (request) => {
                    const results = await this.orm.call("ir.model", "name_search", [], {
                        name: request,
                        limit: 8,
                    });
                    // Fetch technical names for disambiguation
                    const ids = results.map(([id]) => id);
                    const models = ids.length
                        ? await this.orm.read("ir.model", ids, ["model", "name"])
                        : [];
                    const modelMap = {};
                    for (const m of models) {
                        modelMap[m.id] = m;
                    }
                    return results.map(([id, name]) => {
                        const rec = modelMap[id];
                        const technical = rec ? rec.model : "";
                        return {
                            resId: id,
                            label: rec ? `${rec.name} (${technical})` : name,
                            displayName: rec ? `${rec.name} (${technical})` : name,
                            technicalName: technical,
                        };
                    });
                },
            },
        ];
    }

    // --- Analyzer single selectors ---

    onUserSelected(option) {
        this.state.selectedUserId = option.resId;
        this.state.selectedUserDisplay = option.displayName;
        this.state.analysisResult = null;
    }

    onModelSelected(option) {
        this.state.selectedModelDisplay = option.displayName;
        this.state.selectedModelTechnical = option.technicalName;
        this.state.analysisResult = null;
    }

    // --- Matrix multi selectors ---

    onMatrixUserSelected(option) {
        if (this.state.matrixUserIds.includes(option.resId)) {
            return;
        }
        this.state.matrixUserTags.push({
            text: option.displayName,
            resId: option.resId,
            colorIndex: this.state.matrixUserTags.length % 11,
        });
        this.state.matrixUserIds.push(option.resId);
        this.state.matrixData = null;
    }

    removeMatrixUser(userId) {
        const idx = this.state.matrixUserIds.indexOf(userId);
        if (idx !== -1) {
            this.state.matrixUserIds.splice(idx, 1);
            this.state.matrixUserTags.splice(idx, 1);
            this.state.matrixData = null;
        }
    }

    onMatrixModelSelected(option) {
        if (this.state.matrixModelIds.includes(option.resId)) {
            return;
        }
        this.state.matrixModelTags.push({
            text: option.displayName,
            resId: option.resId,
            colorIndex: this.state.matrixModelTags.length % 11,
        });
        this.state.matrixModelIds.push(option.resId);
        this.state.matrixData = null;
    }

    removeMatrixModel(modelId) {
        const idx = this.state.matrixModelIds.indexOf(modelId);
        if (idx !== -1) {
            this.state.matrixModelIds.splice(idx, 1);
            this.state.matrixModelTags.splice(idx, 1);
            this.state.matrixData = null;
        }
    }

    get matrixUserTagsList() {
        return this.state.matrixUserTags.map((tag) => ({
            text: tag.text,
            id: tag.resId,
            colorIndex: tag.colorIndex,
            onDelete: () => this.removeMatrixUser(tag.resId),
        }));
    }

    get matrixModelTagsList() {
        return this.state.matrixModelTags.map((tag) => ({
            text: tag.text,
            id: tag.resId,
            colorIndex: tag.colorIndex,
            onDelete: () => this.removeMatrixModel(tag.resId),
        }));
    }

    // --- Record ID ---

    onRecordIdChange(ev) {
        const value = ev.target.value;
        this.state.recordId = value ? parseInt(value, 10) : null;
    }

    // --- View switching ---

    switchView(viewName) {
        this.state.currentView = viewName;
        if (viewName === "matrix" && !this.state.matrixData) {
            this.loadAccessMatrix();
        }
    }

    // --- Analyzer: CRUD summary (all 4 operations) ---

    async analyzeAccess() {
        if (!this.state.selectedUserId || !this.state.selectedModelTechnical) {
            this.notification.add("Please select both a user and a model", {
                type: "warning",
            });
            return;
        }

        this.state.isAnalyzing = true;
        this.state.analysisResult = null;

        try {
            const modelName = this.state.selectedModelTechnical;

            // Fetch CRUD summary (all 4 operations with conflict detection)
            const crudSummary = await this.orm.call(
                "security.visualizer.analysis",
                "rpc_analyze_crud_summary",
                [modelName, this.state.selectedUserId, this.state.recordId]
            );

            // Fetch record rules per operation
            const ops = ["create", "read", "write", "unlink"];
            const recordRulesPerOp = {};
            for (const op of ops) {
                recordRulesPerOp[op] = await this.orm.call(
                    "security.analyzer",
                    "analyze_record_rules",
                    [modelName, this.state.selectedUserId, op]
                );
            }

            // If record ID is set, simulate access for all 4 operations
            let simulations = null;
            if (this.state.recordId) {
                simulations = {};
                for (const op of ops) {
                    simulations[op] = await this.orm.call(
                        "security.analyzer",
                        "simulate_user_access",
                        [this.state.selectedUserId, modelName, this.state.recordId, op]
                    );
                }
            }

            this.state.analysisResult = {
                crud_summary: crudSummary,
                record_rules_per_op: recordRulesPerOp,
                simulations: simulations,
                context: {
                    userName: this.state.selectedUserDisplay,
                    modelName: this.state.selectedModelDisplay,
                    technicalModel: modelName,
                },
            };

            this.notification.add("Analysis completed", {type: "success"});
        } catch (error) {
            console.error("Analysis error:", error);
            this.notification.add("Analysis failed: " + error.message, {
                type: "danger",
            });
        } finally {
            this.state.isAnalyzing = false;
        }
    }

    // --- Matrix ---

    async loadAccessMatrix() {
        this.state.isLoadingMatrix = true;

        try {
            const userIds =
                this.state.matrixUserIds.length > 0 ? this.state.matrixUserIds : null;
            const modelIds =
                this.state.matrixModelIds.length > 0 ? this.state.matrixModelIds : null;

            const matrixData = await this.orm.call(
                "security.analyzer",
                "get_access_matrix",
                [userIds, modelIds, ["create", "read", "write", "unlink"]]
            );

            this.state.matrixData = matrixData;
        } catch (error) {
            console.error("Matrix loading error:", error);
            this.notification.add("Failed to load access matrix: " + error.message, {
                type: "danger",
            });
        } finally {
            this.state.isLoadingMatrix = false;
        }
    }
}

SecurityVisualizer.template = "security_visualizer.SecurityVisualizer";
SecurityVisualizer.components = {
    AutoComplete,
    TagsList,
    RuleExplainer,
    AccessMatrix,
};

registry.category("actions").add("security_visualizer", SecurityVisualizer);
