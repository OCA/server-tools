// Copyright 2026 Pol Reig <pol.reig@qubiq.es>
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {reactive} from "@odoo/owl";
import {rpcBus} from "@web/core/network/rpc";
import {registry} from "@web/core/registry";

/**
 * The ORM methods through which the web client changes data on the user's
 * behalf. Mirrors USER_EDIT_METHODS on the server: after any of them the undo
 * stack has a new top, and the systray must stop advertising the previous one.
 */
const USER_EDIT_METHODS = new Set([
    "action_archive",
    "action_unarchive",
    "copy",
    "create",
    "toggle_active",
    "unlink",
    "web_save",
    "write",
]);

/**
 * Owns the undo/redo state shared by the hotkeys and the systray item.
 *
 * The hotkeys are registered without `bypassEditableProtection`, so Ctrl+Z
 * inside an input keeps its native "undo my typing" meaning and only reaches
 * the server once the focus is out of a text field.
 */
export const globalUndoService = {
    dependencies: ["orm", "notification", "hotkey", "action"],

    start(env, {orm, notification, hotkey, action}) {
        const state = reactive({undo: false, redo: false, history: [], pending: false});

        async function refresh() {
            Object.assign(
                state,
                await orm.call("global.undo.transaction", "gu_state", [])
            );
        }

        async function apply(direction) {
            if (state.pending) {
                return;
            }
            state.pending = true;
            let result = null;
            try {
                result = await orm.call("global.undo.transaction", "gu_apply_next", [
                    direction,
                ]);
                Object.assign(state, result.state);
            } finally {
                // Released as soon as the server has answered. The reload below
                // is cosmetic, and holding the lock through it would silently
                // swallow a quick second Ctrl+Z.
                state.pending = false;
            }
            notification.add(result.message, {
                type: result.done ? "success" : "warning",
            });
            if (result.done) {
                // The records on screen just changed under the user's feet.
                await action.doAction("soft_reload");
            }
        }

        hotkey.add("control+z", () => apply("undo"), {global: true});
        hotkey.add("control+shift+z", () => apply("redo"), {global: true});

        // Without this the systray keeps showing the step that was on top when
        // it was last opened, so the user reads one label and Ctrl+Z undoes a
        // newer one. Saving a record is precisely what makes it stale.
        rpcBus.addEventListener("RPC:RESPONSE", ({detail}) => {
            const params = detail.data && detail.data.params;
            if (detail.error || !params || params.model === "global.undo.transaction") {
                return;
            }
            // Buttons carry arbitrary method names, so anything action-shaped
            // counts too: gu_state is one small query, a stale label is not.
            const method = params.method || "";
            if (USER_EDIT_METHODS.has(method) || /^(action|button)_/.test(method)) {
                refresh();
            }
        });

        refresh();

        return {
            state,
            refresh,
            undo: () => apply("undo"),
            redo: () => apply("redo"),
            openHistory: () =>
                action.doAction("global_undo.global_undo_transaction_action"),
            openTrash: () =>
                action.doAction("global_undo.global_undo_operation_action_trash"),
        };
    },
};

registry.category("services").add("global_undo", globalUndoService);
