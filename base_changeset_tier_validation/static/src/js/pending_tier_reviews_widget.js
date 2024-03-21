odoo.define("base_changeset_tier_validation.PendingTierReviewsField", function (
    require
) {
    "use strict";

    var AbstractField = require("web.AbstractField");
    var core = require("web.core");
    var field_registry = require("web.field_registry");

    var QWeb = core.qweb;

    var PendingTierReviewsField = AbstractField.extend({
        template: "tier.review.PendingTierReviewsContent",
        events: {
            "click .validate_tier": "_actionValidateTier",
            "click .reject_tier": "_actionRejectTier",
            "click .open_changeset_ref": "_actionOpenChangesetRef",
        },
        start: function () {
            var self = this;
            self._renderPendingTierReviews();
        },
        _renderPendingTierReviews: function () {
            var self = this;
            return this._getPendingTierReviewsData(self.value).then(function () {
                // Hide warning message if a revision is pending
                if (self.reviews.length > 0) {
                    $("#base_tier_validation_warning").hide();
                }
                self.$(".o_review").html(
                    QWeb.render("tier.review.PendingTierReviews", {
                        reviews: self.reviews,
                    })
                );
            });
        },
        _actionValidateTier: function (event) {
            var self = this;
            const review_id = parseInt(event.currentTarget.dataset.review_id);
            this._rpc({
                model: "tier.review",
                method: "validate_tier",
                args: [[review_id]],
            }).then(() => {
                self.trigger_up("reload");
            });
        },
        _actionRejectTier: function (event) {
            var self = this;
            const review_id = parseInt(event.currentTarget.dataset.review_id);
            this._rpc({
                model: "tier.review",
                method: "reject_tier",
                args: [[review_id]],
            }).then(() => {
                self.trigger_up("reload");
            });
        },
        _actionOpenChangesetRef: function (event) {
            // The form of the order line will be opened in modal
            const changeset_ref = event.currentTarget.dataset.changeset_ref;
            const changeset_ref_model = changeset_ref.split(",")[0];
            const changeset_ref_id = parseInt(changeset_ref.split(",")[1]);
            event.preventDefault();
            event.stopPropagation();
            this._rpc({
                model: "changeset.field.rule",
                method: "search_read",
                fields: ["field_name"],
                domain: [
                    ["field_id.relation", "=", changeset_ref_model],
                    ["field_id.model_id.model", "=", this.model],
                ],
            }).then((items) => {
                const field_name = items[0].field_name;
                this.recordData[field_name].data.forEach(function (line) {
                    if (line.res_id === changeset_ref_id) {
                        $("tr[data-id='" + line.id + "']").click();
                    }
                });
            });
        },
        _getPendingTierReviewsData: function (res_ids) {
            var self = this;
            return this._rpc({
                model: "res.users",
                method: "get_pending_tier_reviews",
                args: [res_ids],
            }).then(function (data) {
                self.reviews = data;
            });
        },
    });

    field_registry.add("pending_tier_reviews", PendingTierReviewsField);

    return PendingTierReviewsField;
});
