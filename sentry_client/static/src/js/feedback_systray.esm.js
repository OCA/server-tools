// Copyright 2026 Ledoent
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
//
// Replaces Sentry's autoInject feedback widget — which would collide with
// Odoo's Discuss bubble + activity systray icons — with a navbar launcher
// button that opens the same modal dialog. The trigger is a plain
// `btn btn-link` (the launcher idiom used by the messaging-menu and
// user-menu systray items), not a Dropdown, since clicking it opens a
// Sentry modal rather than an Owl Dropdown menu.
/* global window */

import {Component} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class SentryFeedbackSystray extends Component {
    static template = "sentry_client.FeedbackSystray";
    static props = {};

    setup() {
        this.notification = useService("notification");
        this.title = _t("Report a bug");
    }

    async open() {
        const sdk = window.Sentry;
        const feedback =
            sdk && typeof sdk.getFeedback === "function" ? sdk.getFeedback() : null;
        if (!feedback || typeof feedback.createForm !== "function") {
            this.notification.add(
                _t(
                    "Sentry feedback is not active. Enable Tier 3 → Feedback in " +
                        "Settings, then reload the page."
                ),
                {type: "warning"}
            );
            return;
        }
        // Feedback API in @sentry/browser ≥ 8: createForm() returns a promise
        // for a form instance with explicit appendToDom() + open(). Cache the
        // form instance so repeat clicks don't accumulate DOM nodes.
        if (!this._form) {
            this._form = await feedback.createForm();
            this._form.appendToDom();
        }
        this._form.open();
    }
}

registry
    .category("systray")
    .add(
        "sentry_client.FeedbackButton",
        {Component: SentryFeedbackSystray},
        {sequence: 100}
    );
