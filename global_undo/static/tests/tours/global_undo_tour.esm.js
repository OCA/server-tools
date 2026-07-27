// Copyright 2026 Pol Reig <pol.reig@qubiq.es>
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
/* global document */

import {isMacOS} from "@web/core/browser/feature_detection";
import {registry} from "@web/core/registry";

/**
 * Drives the systray in a real browser: undo the contact created by the test
 * with the button, redo it, then undo it again with the keyboard shortcut and
 * check the history reflects it.
 */
registry.category("web_tour.tours").add("global_undo_tour", {
    url: "/odoo",
    steps: () => [
        {
            // The button names the step it would act on, which is only correct
            // if the systray state was refreshed after the contact was created.
            content: "the systray knows what Ctrl+Z would undo",
            trigger:
                ".o_global_undo_undo[title='Undo (Ctrl+Z): Created Contact: GU Tour Partner']",
        },
        {
            content: "nothing has been undone yet, so there is nothing to redo",
            trigger: ".o_global_undo_redo[disabled]",
        },
        {
            content: "undo the contact creation",
            trigger: ".o_global_undo_undo",
            run: "click",
        },
        {
            content: "the server confirms the undo",
            trigger:
                ".o_notification:contains('Undone: Created Contact: GU Tour Partner')",
        },
        {
            content: "the redo button now names the step it would replay",
            trigger:
                ".o_global_undo_redo[title='Redo (Ctrl+Shift+Z): Created Contact: GU Tour Partner']",
            run: "click",
        },
        {
            content: "the server confirms the redo",
            trigger:
                ".o_notification:contains('Redone: Created Contact: GU Tour Partner')",
        },
        {
            // So the next assertion can only match the keyboard undo.
            content: "dismiss the notifications",
            trigger: "body",
            run: () => {
                document
                    .querySelectorAll(".o_notification_close")
                    .forEach((button) => button.click());
            },
        },
        {
            // Waiting for the last notification to go also waits for the reload
            // the redo triggered, which would otherwise put the focus back in
            // the search field a moment after it was dropped.
            content: "wait for the screen to settle, then leave any text field",
            trigger: "body:not(:has(.o_notification))",
            run: () => document.activeElement && document.activeElement.blur(),
        },
        {
            // Outside a text field, where Ctrl+Z no longer means "undo my typing".
            content: "undo again, this time with the keyboard",
            trigger: "body",
            // Odoo's hotkey service maps "control" to Cmd on macOS.
            run: `press ${isMacOS() ? "Meta" : "Control"}+z`,
        },
        {
            content: "the shortcut reached the server too",
            trigger:
                ".o_notification:contains('Undone: Created Contact: GU Tour Partner')",
        },
        {
            content: "open the history",
            trigger: ".o_global_undo .fa-history",
            run: "click",
        },
        {
            content: "the step is listed as undone",
            trigger:
                ".o_global_undo_entry.text-decoration-line-through:contains('GU Tour Partner')",
        },
    ],
});
