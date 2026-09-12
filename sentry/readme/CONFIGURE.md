The following additional configuration options can be added to your Odoo
configuration file:

[TABLE]

Other [client
arguments](https://docs.sentry.io/platforms/python/configuration/) can
be configured by prepending the argument name with *sentry\_* in your
Odoo config file. Currently supported additional client arguments are:
`with_locals, max_breadcrumbs, release, environment, server_name, shutdown_timeout, in_app_include, in_app_exclude, default_integrations, dist, sample_rate, send_default_pii, http_proxy, https_proxy, request_bodies, debug, attach_stacktrace, ca_certs, propagate_traces, traces_sample_rate, auto_enabling_integrations`.

## Environment variables

Every option above can also be set through an environment variable, named after
the option it carries with an `ODOO_` prefix: `sentry_dsn` becomes
`ODOO_SENTRY_DSN`, `sentry_traces_sample_rate` becomes
`ODOO_SENTRY_TRACES_SAMPLE_RATE`. This is the same shape *queue_job* uses for
`ODOO_QUEUE_JOB_*`.

Both sources stay supported and are merged per option, the environment winning
where the two disagree. An existing `[sentry]` section keeps working as it is,
and a deployment that would rather not ship a configuration file at all can set
everything through the environment instead.

The `ODOO_` prefix is what keeps these apart from the `SENTRY_*` variables
*sentry-sdk* reads on its own. `SENTRY_DSN` addresses whichever process the
library runs in, so it is left alone rather than reused here.

Two reasons a container may prefer the environment:

- Odoo reads only `[options]` from its configuration file, and logs
  `unknown option ... in the config file` for anything there it does not know.
  The `[sentry]` section is quiet, but it exists only because these options had
  to leave `[options]` for that reason.
- `odoo-bin -s` rewrites the configuration file out of its own options, which
  drops every other section, `[sentry]` included.

## Example Odoo configuration

Below is an example of Odoo configuration file with *Odoo Sentry*
options:

    [options]
    (...)
    server_wide_modules = web,sentry

    [sentry]
    sentry_dsn = https://<public_key>:<secret_key>@sentry.example.com/<project id>
    sentry_enabled = true
    sentry_logging_level = warn
    sentry_exclude_loggers = werkzeug
    sentry_ignore_exceptions = odoo.exceptions.AccessDenied,
        odoo.exceptions.AccessError,odoo.exceptions.MissingError,
        odoo.exceptions.RedirectWarning,odoo.exceptions.UserError,
        odoo.exceptions.ValidationError,odoo.exceptions.Warning,
        odoo.exceptions.except_orm
    sentry_include_context = true
    sentry_environment = production
    sentry_release = 1.3.2
    sentry_odoo_dir = /home/odoo/odoo/
    sentry_startup_message = true

## Example environment

The same setup, with `server_wide_modules` left in the configuration file
because that one is Odoo's own option:

    ODOO_SENTRY_DSN=https://<public_key>:<secret_key>@sentry.example.com/<project id>
    ODOO_SENTRY_ENABLED=true
    ODOO_SENTRY_LOGGING_LEVEL=warn
    ODOO_SENTRY_EXCLUDE_LOGGERS=werkzeug
    ODOO_SENTRY_INCLUDE_CONTEXT=true
    ODOO_SENTRY_ENVIRONMENT=production
    ODOO_SENTRY_RELEASE=1.3.2
    ODOO_SENTRY_ODOO_DIR=/home/odoo/odoo/
    ODOO_SENTRY_STARTUP_MESSAGE=true
