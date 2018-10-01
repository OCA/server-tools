* Since version ``2.0.0``, some features have been deprecated.
  When you upgrade from previous versions, these features will be kept for
  backwards compatibility, but beware! They are buggy!

  If you install this addon from scratch, these features are disabled by
  default.

  To force enabling or disabling the deprecated features, set a configuration
  parameter called ``module_auto_update.enable_deprecated`` to either ``1``
  or ``0``. It is recommended that you disable them.

  Keep in mind that from this version, all upgrades are assumed to run in a
  separate odoo instance, dedicated exclusively to upgrade Odoo.

* When migrating the addon to new versions, the deprecated features should be
  removed. To make it simple all deprecated features are found in files
  suffixed with ``_deprecated``.
