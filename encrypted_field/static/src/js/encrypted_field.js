/** @odoo-module **/

import {registry} from "@web/core/registry";
import {CharField, charField} from "@web/views/fields/char/char_field";
import {useService} from "@web/core/utils/hooks";
import {_t} from "@web/core/l10n/translation";

const {useState, onWillUpdateProps} = owl;

export class EncryptedField extends CharField {
    static template = "encrypted_field.EncryptedField";

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.lastRecordId = this.props.record.resId;
        this.state = useState({
            revealed: false,
            unmaskedValue: null,
            loading: false,
            editing: false,
            hasLocalEdit: false,
        });

        // Reset state when record changes (navigation)
        onWillUpdateProps((nextProps) => {
            if (nextProps.record.resId !== this.lastRecordId) {
                this.state.revealed = false;
                this.state.unmaskedValue = null;
                this.state.editing = false;
                this.state.hasLocalEdit = false;
                this.lastRecordId = nextProps.record.resId;
            }
        });
    }

    get displayValue() {
        if (this.state.revealed && this.state.unmaskedValue !== null) {
            return this.state.unmaskedValue;
        }
        return this.props.record.data[this.props.name] || "";
    }

    async onRevealClick() {
        if (this.state.revealed) {
            // Hide the value but keep local edits
            this.state.revealed = false;
            this.state.editing = false;
            // Don't clear unmaskedValue if we have local edits
            return;
        }

        // If we have a local edit, just reveal it without fetching
        if (this.state.hasLocalEdit && this.state.unmaskedValue !== null) {
            this.state.revealed = true;
            this.state.editing = true;
            return;
        }

        // Fetch from server
        this.state.loading = true;
        try {
            const result = await this.orm.call(
                this.props.record.resModel,
                "get_unmasked_value",
                [this.props.record.resId, this.props.name]
            );
            this.state.unmaskedValue = result;
            this.state.revealed = true;
            this.state.editing = true;
        } catch (error) {
            this.notification.add(
                error.data?.message || _t("You don't have access to view this value."),
                {type: "danger"}
            );
        } finally {
            this.state.loading = false;
        }
    }

    onInputChange(ev) {
        const newValue = ev.target.value;
        this.state.unmaskedValue = newValue;
        this.state.hasLocalEdit = true;
        // Update the record with the new value
        this.props.record.update({[this.props.name]: newValue});
    }

    onAddClick() {
        // Enable editing mode for empty fields
        this.state.editing = true;
        this.state.unmaskedValue = "";
        this.state.hasLocalEdit = true;
    }
}

export const encryptedField = {
    ...charField,
    component: EncryptedField,
    displayName: _t("Encrypted"),
    supportedTypes: ["char", "text"],
};

registry.category("fields").add("encrypted", encryptedField);
