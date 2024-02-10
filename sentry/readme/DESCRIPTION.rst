This module allows painless `Sentry <https://sentry.io/>`__ integration with
Odoo.

=============================  ====================================================================  ==========================================================
        Option                                          Description                                                         Default
=============================  ====================================================================  ==========================================================
``sentry_dsn``                 Sentry *Data Source Name*. You can find this value in your Sentry     ``''``
                               project configuration. Typically it looks something like this:
                               *https://<public_key>:<secret_key>@sentry.example.com/<project id>*
                               This is the only required option in order to use the module.

``sentry_enabled``             Whether or not Sentry logging is enabled.                             ``False``

``sentry_logging_level``       The minimal logging level for which to send reports to Sentry.        ``warn``
                               Possible values: *notset*, *debug*, *info*, *warn*, *error*,
                               *critical*. It is recommended to have this set to at least *warn*,
                               to avoid spamming yourself with Sentry events.

``sentry_exclude_loggers``     A string of comma-separated logger names which should be excluded     ``werkzeug``
                               from Sentry.

``sentry_ignored_exceptions``  A string of comma-separated exceptions which should be ignored.       ``odoo.exceptions.AccessDenied,
                               You can use a star symbol (*) at the end, to ignore all exceptions    odoo.exceptions.AccessError,
                               from a module, eg.: *odoo.exceptions.**.                              odoo.exceptions.DeferredException,
                                                                                                     odoo.exceptions.MissingError,
                                                                                                     odoo.exceptions.RedirectWarning,
                                                                                                     odoo.exceptions.UserError,
                                                                                                     odoo.exceptions.ValidationError,
                                                                                                     odoo.exceptions.Warning,
                                                                                                     odoo.exceptions.except_orm``

``sentry_include_context``     If enabled, additional context data will be extracted from current    ``True``
                               HTTP request and user session (if available). This has no effect
                               for Cron jobs, as no request/session is available inside a Cron job.

``sentry_release``             Explicitly define a version to be sent as the release version to
                               Sentry. Useful in conjuntion with Sentry's "Resolve in the next
                               release"-functionality. Also useful if your production deployment
                               does not include any Git context from which a commit might be read.
                               Overrides *sentry_odoo_dir*.

``sentry_odoo_dir``            Absolute path to your Odoo installation directory. This is optional
                               and will only be used to extract the Odoo Git commit, which will be
                               sent to Sentry, to allow to distinguish between Odoo updates.
                               Overridden by *sentry_release*
=============================  ====================================================================  ==========================================================

Other `client arguments
<https://docs.sentry.io/platforms/python/configuration/>`_ can be
configured by prepending the argument name with *sentry_* in your Odoo config
file. Currently supported additional client arguments are: ``include_local_variables,
max_breadcrumbs, release, environment, server_name, shutdown_timeout,
in_app_include, in_app_exclude, default_integrations, dist, sample_rate,
send_default_pii, http_proxy, https_proxy, max_request_body_size, debug,
attach_stacktrace, ca_certs, propagate_traces, traces_sample_rate,
auto_enabling_integrations``.

Example Odoo configuration
--------------------------

Below is an example of Odoo configuration file with *Odoo Sentry* options::

    [options]
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

The options can be also set as environment variables, with the format ODOO_{option_name_in_uppercase}. For example ODOO_SENTRY_ENABLED
