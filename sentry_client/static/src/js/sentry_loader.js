// Copyright 2026 Ledoent
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
/* global window, document, console, fetch, crypto, setInterval, clearInterval */

(function () {
    "use strict";

    const CONFIG_URL = "/sentry_client/config.json";

    function loadScript(src) {
        return new Promise((resolve, reject) => {
            const tag = document.createElement("script");
            tag.src = src;
            tag.crossOrigin = "anonymous";
            tag.async = true;
            tag.onload = () => resolve();
            tag.onerror = () => reject(new Error(`Failed to load ${src}`));
            document.head.appendChild(tag);
        });
    }

    async function fetchConfig() {
        try {
            const resp = await fetch(CONFIG_URL, {credentials: "same-origin"});
            if (!resp.ok) {
                return null;
            }
            if (!resp.headers.get("content-type")?.includes("application/json")) {
                return null;
            }
            return await resp.json();
        } catch (err) {
            console.warn("[sentry_client] config fetch failed:", err);
            return null;
        }
    }

    function buildIntegrations(Sentry, conf, replayOn) {
        const integrations = [];
        if (
            conf.integrations.tracing &&
            typeof Sentry.browserTracingIntegration === "function"
        ) {
            integrations.push(Sentry.browserTracingIntegration());
        }
        if (replayOn) {
            // Privacy posture: defaults already mask all text + inputs + media.
            // Add explicit selectors for Odoo password fields, user signature
            // HTML, and avatar imgs; deny network-body capture for auth.
            integrations.push(
                Sentry.replayIntegration({
                    mask: [
                        ".o_password_field",
                        "[data-fieldname='signature']",
                        "img.o_avatar",
                    ],
                    networkDetailDenyUrls: [
                        /\/web\/session\/authenticate/,
                        /\/res\.users\/change_password/,
                    ],
                })
            );
        }
        if (
            conf.integrations.feedback &&
            typeof Sentry.feedbackIntegration === "function"
        ) {
            // AutoInject: false — the floating bottom-right widget would
            // collide with Odoo's Discuss bubble and activity systray icons.
            // The companion sentry_client.FeedbackSystray component opens
            // the modal dialog from a navbar button instead.
            integrations.push(Sentry.feedbackIntegration({autoInject: false}));
        }
        if (
            conf.integrations.profiling &&
            typeof Sentry.browserProfilingIntegration === "function"
        ) {
            integrations.push(Sentry.browserProfilingIntegration());
        }
        if (
            conf.integrations.logs &&
            typeof Sentry.consoleLoggingIntegration === "function"
        ) {
            integrations.push(Sentry.consoleLoggingIntegration());
        }
        return integrations;
    }

    // Drop the global-handlers re-capture of errors the OWL boundary already
    // sent. Our boundary handler marks the wrapping error with
    // `__sentry_owl_captured__` before calling captureException, and then
    // `window.onunhandledrejection` fires later for the same rejection. This
    // hook strips that second event so each OWL crash surfaces as one Sentry
    // issue (carrying the `owl: true` tag) rather than two.
    function dropDuplicateOwlRejection(event, hint) {
        const original = hint && hint.originalException;
        if (!original) {
            return event;
        }
        // The OWL wrapping error carries the marker we set before capture.
        // Its cause may carry it too (when the SDK unwraps via LinkedErrors).
        const owlMarked =
            original.__sentry_owl_captured__ ||
            (original.cause && original.cause.__sentry_owl_captured__);
        const mech =
            event.exception &&
            event.exception.values &&
            event.exception.values[0] &&
            event.exception.values[0].mechanism;
        const isGlobalRejection =
            mech && mech.type === "auto.browser.global_handlers.onunhandledrejection";
        if (owlMarked && isGlobalRejection) {
            return null;
        }
        return event;
    }

    function buildInitOptions(Sentry, conf, replayOn) {
        const opts = {
            dsn: conf.dsn,
            release: conf.release || undefined,
            environment: conf.environment || undefined,
            integrations: buildIntegrations(Sentry, conf, replayOn),
            beforeSend: dropDuplicateOwlRejection,
        };
        if (conf.integrations.tracing) {
            opts.tracesSampleRate = conf.traces_sample_rate;
        }
        if (replayOn) {
            opts.replaysSessionSampleRate = conf.replay_session_sample_rate;
            opts.replaysOnErrorSampleRate = conf.replay_error_sample_rate;
        }
        if (conf.integrations.profiling) {
            opts.profilesSampleRate = conf.profiles_sample_rate;
        }
        return opts;
    }

    function shouldEnableReplay(conf) {
        if (!conf.integrations.replay) {
            return false;
        }
        if (conf.replay_optout) {
            return false;
        }
        return typeof window.Sentry?.replayIntegration === "function";
    }

    function attachUserContext(Sentry, conf) {
        if (!conf.user_id || typeof Sentry.setUser !== "function") {
            return;
        }
        // Only the numeric uid leaves the server via /sentry_client/config.json;
        // Sentry clusters events by id alone. Email enrichment can be done
        // server-side in the OCA `sentry` module's before_send hook if needed.
        Sentry.setUser({id: conf.user_id});
        if (Array.isArray(conf.groups) && conf.groups.length) {
            Sentry.setTag("odoo.groups", conf.groups.join(","));
        }
        if (Array.isArray(conf.categories) && conf.categories.length) {
            Sentry.setTag("odoo.category", conf.categories.join(","));
        }
    }

    // Coarse surface classifier — backend webclient, customer portal, or
    // public website — derived from the URL prefix at SDK init time. Lets
    // Sentry queries filter cleanly across the three places JS errors
    // originate without leaning on the implicit "has odoo.model tag"
    // signal (which only the backend webclient sets, via the action
    // manager subscription below).
    function deriveSurface() {
        const path = window.location.pathname;
        if (path.startsWith("/odoo") || path.startsWith("/web")) {
            return "backend";
        }
        if (path.startsWith("/my")) {
            return "portal";
        }
        return "frontend";
    }

    // Stable per-tab UUID, persisted in sessionStorage. Sentry's own replay
    // session id is also per-tab, but ours is broader: every event (errors,
    // transactions, breadcrumbs) carries it, so the harvester can split a
    // single user's parallel windows into distinct workflow streams.
    function getOrCreateTabId() {
        const KEY = "sentry_client.tab_id";
        try {
            let id = window.sessionStorage.getItem(KEY);
            if (!id) {
                id =
                    typeof crypto !== "undefined" && crypto.randomUUID
                        ? crypto.randomUUID()
                        : `tab-${Date.now()}-${Math.random()
                              .toString(36)
                              .slice(2, 10)}`;
                window.sessionStorage.setItem(KEY, id);
            }
            return id;
        } catch {
            // Private-mode browsers can refuse sessionStorage; degrade
            // gracefully to a per-page-load UUID (no cross-reload continuity).
            return `tab-fallback-${Date.now()}`;
        }
    }

    // Subscribe to Odoo's web-client action bus; on each action transition,
    // re-derive a compact workflow_id and set it as a Sentry tag. The web
    // client may not be mounted yet when this runs — poll briefly.
    function wireWorkflowTracking(Sentry) {
        let tries = 0;
        const interval = setInterval(() => {
            tries += 1;
            const root =
                window.odoo &&
                window.odoo.__WOWL_DEBUG__ &&
                window.odoo.__WOWL_DEBUG__.root;
            const bus = root && root.env && root.env.bus;
            const actionService =
                root && root.env && root.env.services && root.env.services.action;
            if (!bus || !actionService) {
                if (tries > 60) {
                    // 60 * 500ms = 30s — give up; portal/public users have no
                    // backend action manager and that's fine.
                    clearInterval(interval);
                }
                return;
            }
            clearInterval(interval);
            const apply = () => {
                const cc = actionService.currentController;
                if (!cc || !cc.action) {
                    return;
                }
                const action = cc.action;
                const tags = {
                    "odoo.model": action.res_model || "",
                    "odoo.action_id": action.id || 0,
                    "odoo.view_type": cc.view && cc.view.type ? cc.view.type : "",
                };
                tags.workflow_id = `${tags["odoo.action_id"]}|${tags["odoo.model"]}|${tags["odoo.view_type"]}`;
                Sentry.setTags(tags);
            };
            apply();
            bus.addEventListener("ACTION_MANAGER:UPDATE", apply);
        }, 500);
    }

    async function initSentryClient() {
        const conf = await fetchConfig();
        if (!conf || !conf.enabled || !conf.dsn || !conf.bundle_url) {
            return;
        }
        try {
            await loadScript(conf.bundle_url);
            if (conf.profiling_addon_url) {
                await loadScript(conf.profiling_addon_url);
            }
        } catch (err) {
            console.warn("[sentry_client] bundle load failed:", err);
            return;
        }
        const Sentry = window.Sentry;
        if (!Sentry || typeof Sentry.init !== "function") {
            return;
        }
        const replayOn = shouldEnableReplay(conf);
        Sentry.init(buildInitOptions(Sentry, conf, replayOn));
        Sentry.setTag("tab_id", getOrCreateTabId());
        Sentry.setTag("surface", deriveSurface());
        attachUserContext(Sentry, conf);
        wireWorkflowTracking(Sentry);
    }

    // Defer to avoid blocking first paint; gate via DOMContentLoaded so the
    // controller's authenticated context (replay opt-out, etc.) is fresh.
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initSentryClient, {
            once: true,
        });
    } else {
        initSentryClient();
    }
})();
