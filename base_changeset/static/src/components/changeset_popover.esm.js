/** @odoo-module */

import {Component} from "@odoo/owl";
import {FormLabel} from "@web/views/form/form_label";
import Popover from "web.Popover";

export class BaseChangesetPopover extends Popover {
    /*
      Call the ORM to accept the change and refresh the form view
      to update the field value.
    */
    async applyChange(change_id) {
        await this.props.record.model.orm.call(
            "record.changeset.change",
            "apply",
            [[change_id]],
            {
                context: {set_change_by_ui: true},
            }
        );
        this._close();
        // Save the record first to prevent losing unsaved data on load.
        await this.props.record.save();
        await this.props.record.load();
        await this.props.record.model.notify();
    }
    /*
      Call the ORM to reject the change and only update the record's pending changes.
    */
    async rejectChange(change_id) {
        await this.props.record.model.orm.call(
            "record.changeset.change",
            "cancel",
            [[change_id]],
            {
                context: {set_change_by_ui: true},
            }
        );
        this._close();
        this.props.record.changesetChanges =
            await this.props.record.fetchChangesetChanges();
        this.props.record.model.notify();
    }
}
BaseChangesetPopover.template = "base_changeset.ChangesetPopover";
BaseChangesetPopover.props = ["fieldName", "popoverClass", "record", "title"];

export class BaseChangesetPopoverWrapper extends Component {}
BaseChangesetPopoverWrapper.components = {BaseChangesetPopover};
BaseChangesetPopoverWrapper.template = "base_changeset.ChangesetPopoverWrapper";

FormLabel.components = FormLabel.components || {};
Object.assign(FormLabel.components, {BaseChangesetPopoverWrapper});
