/* @odoo-module */

import {Record} from "@web/views/basic_relational_model";
import {patch} from "@web/core/utils/patch";

patch(Record.prototype, "base_changeset.Record", {
    /* Call the ORM to get this record's changeset changes */
    async fetchChangesetChanges() {
        return this.model.orm.call(
            "record.changeset.change",
            "get_changeset_changes_by_field",
            [this.resModel, this.resId]
        );
    },
    /* After loading the form's record data, fetch the changeset changes */
    async load() {
        await this._super(...arguments);
        if (this.__viewType === "form" && this.resId) {
            this.changesetChanges = await this.fetchChangesetChanges();
        }
    },
    /* Call the ORM to get this record's changeset changes after the form is modified */
    async save() {
        const isSaved = await this._super(...arguments);
        if (this.__viewType === "form" && this.resId) {
            this.changesetChanges = await this.fetchChangesetChanges();
            this.model.notify();
        }
        return isSaved;
    },
});
