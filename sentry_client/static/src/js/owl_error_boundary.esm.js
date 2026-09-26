// Copyright 2026 Ledoent
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
//
// Backend capture path: Odoo's error service routes every window error and
// unhandled rejection through the error_handlers registry, so sentry_loader.js
// drops the SDK's own global handlers when this service is present.
/* global window */

import {
    ConnectionAbortedError,
    ConnectionLostError,
    RPCError,
    RequestEntityTooLargeError,
} from "@web/core/network/rpc";
import {registry} from "@web/core/registry";

// Reported by the server-side `sentry` module (session expiry is an RPCError)
// or surfaced by Odoo's own dialogs; none of them is a browser-side bug.
const SERVER_SIDE_ERRORS = [
    RPCError,
    ConnectionLostError,
    ConnectionAbortedError,
    RequestEntityTooLargeError,
];

// Replay in buffer mode (on-error sampling) only uploads when the SDK
// captures an exception, which server-side errors deliberately don't do.
// Flush it here so the server-side event has a recording to link to — the
// two share the trace propagated on the request.
function flushReplay(sdk) {
    const replay = typeof sdk.getReplay === "function" && sdk.getReplay();
    if (replay && typeof replay.flush === "function") {
        Promise.resolve(replay.flush()).catch(() => undefined);
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
    const cause = originalError || error;
    if (SERVER_SIDE_ERRORS.some((cls) => cause instanceof cls)) {
        const data = cause.data || {};
        sdk.addBreadcrumb({
            category: "odoo.rpc",
            level: "error",
            message: `${cause.name}: ${data.message || cause.message || ""}`.slice(
                0,
                200
            ),
            data: {exception: data.name, model: cause.model},
        });
        if (cause instanceof RPCError) {
            flushReplay(sdk);
        }
        return false;
    }
    // Capture the wrapping error: LinkedErrors expands `.cause` in one event.
    const target = error || originalError;
    const extra = buildExtra(target);
    sdk.captureException(target, {
        tags: {owl: Boolean(extra.component_tree)},
        extra,
    });
    // Odoo's own handlers (Oops! dialog, retry chain) still run.
    return false;
}

registry.category("error_handlers").add("sentry_client.owl", sentryHandler);
