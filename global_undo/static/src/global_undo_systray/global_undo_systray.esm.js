// Copyright 2026 Pol Reig <pol.reig@qubiq.es>
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {Component, useState} from "@odoo/owl";
import {deserializeDateTime, formatDateTime} from "@web/core/l10n/dates";
import {Dropdown} from "@web/core/dropdown/dropdown";
import {DropdownItem} from "@web/core/dropdown/dropdown_item";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class GlobalUndoSystray extends Component {
    static template = "global_undo.GlobalUndoSystray";
    static components = {Dropdown, DropdownItem};
    static props = {};

    setup() {
        this.undoService = useService("global_undo");
        // UseState, not the bare reactive object: without subscribing here the
        // systray would keep rendering whatever it saw on its first paint.
        this.state = useState(this.undoService.state);
    }

    /**
     * What the button would act on right now. Naming the step is the whole
     * point of keeping the state fresh: a shortcut that silently undoes
     * something other than what the user has in mind is worse than no shortcut.
     */
    buttonTitle(direction) {
        const step = this.state[direction];
        if (direction === "undo") {
            return step
                ? _t("Undo (Ctrl+Z): %s", step.name)
                : _t("Nothing to undo (Ctrl+Z)");
        }
        return step
            ? _t("Redo (Ctrl+Shift+Z): %s", step.name)
            : _t("Nothing to redo (Ctrl+Shift+Z)");
    }

    formatDate(value) {
        return value ? formatDateTime(deserializeDateTime(value)) : "";
    }

    onOpened() {
        // The history changes with every save the user makes elsewhere.
        this.undoService.refresh();
    }
}

registry
    .category("systray")
    .add("global_undo.systray", {Component: GlobalUndoSystray}, {sequence: 20});
