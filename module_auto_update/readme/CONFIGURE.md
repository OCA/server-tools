This module supports the following system parameters:

- `module_auto_update.exclude_patterns`: comma-separated list of file
  name patterns to ignore when computing addon checksums. Defaults to
  `*.pyc,*.pyo,i18n/*.pot,i18n_extra/*.pot,static/*,tests/*`. Filename patterns
  must be compatible with the python `fnmatch` function.

In addition to the above pattern, .po files corresponding to languages
that are not installed in the Odoo database are ignored when computing
checksums.
