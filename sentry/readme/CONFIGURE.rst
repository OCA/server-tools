The following additional configuration options can be added to your Odoo
configuration file:

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

``sentry_processors``          A string of comma-separated processor classes which will be applied   ``raven.processors.SanitizePasswordsProcessor,
                               on an event before sending it to Sentry.                              odoo.addons.sentry.logutils.SanitizeOdooCookiesProcessor``

``sentry_transport``           Transport class which will be used to send events to Sentry.          ``threaded``
                               Possible values: *threaded*: spawns an async worker for processing
                               messages, *synchronous*: a synchronous blocking transport;
                               *requests_threaded*: an asynchronous transport using the *requests*
                               library; *requests_synchronous* - blocking transport using the
                               *requests* library.

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
<https://docs.sentry.io/clients/python/advanced/#client-arguments>`_ can be
configured by prepending the argument name with *sentry_* in your Odoo config
file. Currently supported additional client arguments are: ``install_sys_hook,
include_paths, exclude_paths, machine, auto_log_stacks, capture_locals,
string_max_length, list_max_length, site, include_versions, environment``.

Example Odoo configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Below is an example of Odoo configuration file with *Odoo Sentry* options::

    [options]
    sentry_dsn = https://<public_key>:<secret_key>@sentry.example.com/<project id>
    sentry_enabled = true
    sentry_logging_level = warn
    sentry_exclude_loggers = werkzeug
    sentry_ignore_exceptions = odoo.exceptions.AccessDenied,odoo.exceptions.AccessError,odoo.exceptions.MissingError,odoo.exceptions.RedirectWarning,odoo.exceptions.UserError,odoo.exceptions.ValidationError,odoo.exceptions.Warning,odoo.exceptions.except_orm
    sentry_processors = raven.processors.SanitizePasswordsProcessor,odoo.addons.sentry.logutils.SanitizeOdooCookiesProcessor
    sentry_transport = threaded
    sentry_include_context = true
    sentry_environment = production
    sentry_auto_log_stacks = false
    sentry_odoo_dir = /home/odoo/odoo/
    sentry_release = 1.3.2
