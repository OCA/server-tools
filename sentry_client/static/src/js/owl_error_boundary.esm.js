// Copyright 2026 Ledoent
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
//
// OWL-aware error handler — registers a Sentry-aware entry in Odoo's
// @web/core/error_handlers registry so component-tree context lands in
// Sentry events alongside the existing Odoo Oops! dialog flow.
//
// Backend-only: OWL lives under web.assets_backend. Frontend portal/website
// runs on plain templates with no OWL tree.
/* global window */

import {registry} from "@web/core/registry";

// Walk the `.cause` chain marking each error with the dedup sentinel that
// sentry_loader.js's beforeSend hook reads. Odoo wraps the OwlError in an
// UncaughtPromiseError before our handler runs, but the `unhandledrejection`
// event's `reason` is the INNER OwlError — so a marker only on `target` would
// miss it. Capping at 8 levels guards against pathological cycles. Frozen
// error objects (rare) silently no-op via try/catch.
function markChain(target) {
    let cur = target;
    for (let i = 0; i < 8 && cur; i++) {
        try {
            cur.__sentry_owl_captured__ = true;
        } catch {
            // Frozen error object: best-effort only.
        }
        cur = cur.cause;
    }
}

function buildExtra(target) {
    const extra = {
        event_type: target && target.constructor && target.constructor.name,
    };
    const ct =
        (target && target.componentTree) ||
        (target && target.cause && target.cause.componentTree);
    if (ct) {
        extra.component_tree = ct;
    }
    if (target && target.props !== undefined) {
        extra.props = target.props;
    }
    return extra;
}

function sentryHandler(env, error, originalError) {
    const sdk = window.Sentry;
    if (!sdk || typeof sdk.captureException !== "function") {
        return false;
    }
    // Capture the WRAPPING error so Sentry's built-in LinkedErrors integration
    // expands `.cause` into nested exception_id entries inside ONE event. If
    // we captured originalError directly here, the global onunhandledrejection
    // handler would still fire on the wrapping error (Odoo's chain doesn't
    // swallow it), yielding two separate issues for the same crash. With this
    // approach Sentry's Dedupe integration drops the global re-capture (same
    // outer message + stacktrace).
    const target = error || originalError;
    markChain(target);
    sdk.captureException(target, {
        tags: {owl: true},
        extra: buildExtra(target),
    });
    // Return false so Odoo's other handlers also run (the user still sees
    // the standard Oops! dialog, the network request retry chain, etc.).
    return false;
}

registry.category("error_handlers").add("sentry_client.owl", sentryHandler);
