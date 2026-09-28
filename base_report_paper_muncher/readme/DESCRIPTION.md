This module integrates [Paper Muncher](https://odoo.github.io/paper-muncher/) as
the PDF rendering engine for QWeb reports. When the `paper-muncher` binary is
available on the system, it replaces wkhtmltopdf as the default engine for PDF
generation.

Main features:

- Automatic detection of the `paper-muncher` binary in `PATH` or in
  `/opt/paper-muncher/bin/paper-muncher`
- Globally configurable PDF engine via the `report.pdf_engine` system parameter
- Multi-page header and footer support and `report.paperformat` integration
- Transparent fallback to wkhtmltopdf when Paper Muncher is not installed
- HTTP-over-pipe communication between Odoo and the Paper Muncher subprocess,
  so report assets are served with Odoo permissions

This module depends on:

- Odoo modules: `base`, `web`
- Python package: `h11`
- System binary: `paper-muncher` from
  [GitHub releases](https://github.com/odoo/paper-muncher/releases)
