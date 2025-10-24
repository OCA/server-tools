import {Component, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class ReviewsTable extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({
            collapse: false,
        });
    }

    _getReviewData() {
        const records = this.env.model.root.data.review_ids.records;
        return records.map((record) => record.data);
    }

    onToggleCollapse(ev) {
        const panelHeading = ev.currentTarget.closest(".panel-heading");
        const collapseDiv = panelHeading.nextElementSibling.matches("div#collapse1")
            ? panelHeading.nextElementSibling
            : null;
        if (!collapseDiv) {
            return;
        }
        if (this.state.collapse) {
            collapseDiv.style.display = "none";
        } else {
            collapseDiv.style.display = "block";
        }
        this.state.collapse = !this.state.collapse;
    }
}

ReviewsTable.template = "base_tier_validation.Collapse";

export const reviewsTableComponent = {
    component: ReviewsTable,
    supportedTypes: ["one2many"],
    relatedFields: [
        {name: "id", type: "integer"},
        {name: "sequence", type: "integer"},
        {name: "name", type: "char"},
        {name: "display_status", type: "char"},
        {name: "todo_by", type: "char"},
        {name: "status", type: "char"},
        {name: "reviewed_formated_date", type: "char"},
        {name: "comment", type: "char"},
        {name: "requested_by_name", type: "char"},
        {name: "done_by_name", type: "char"},
    ],
};

registry.category("fields").add("form.tier_validation", reviewsTableComponent);
