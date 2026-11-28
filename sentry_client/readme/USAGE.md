Once Tier 0 is enabled and a DSN is in `[sentry]`, the next page load injects
the (vendored) Sentry browser SDK and starts capturing errors. No further
user action needed.

To verify the integration:

1. Open the browser dev tools console on any Odoo page.
2. Run `throw new Error("sentry_client smoke test")`.
3. The error appears in your Sentry project within a few seconds, tagged with
   your Odoo `user.id`, `release`, and `environment`.

## Per-user opt-out

Top-right avatar → My Profile → Preferences → Privacy →
**Disable Sentry session replay**. Saves to your own user record. The
opt-out only suppresses session replay; basic error capture (Tier 0)
still fires.

## OWL component context

When the backend OWL stack raises an exception (the usual "Oops!" dialog
you see in the Odoo web client), the resulting Sentry event automatically
carries:

- `tags.owl = true`
- `extra.component_tree` — the OWL component path

No configuration needed — the OCA `sentry_client` module registers an
entry in `@web/core/error_handlers` at install time. Standard Odoo error
UX is unaffected.
