Provide up to date [Fontawesome](http://fontawesome.io/) resources.

Current version: 6.7.2 (the version of this module matches it).

Odoo's HTML editor lists the Font Awesome icons it can insert, and its email
conversion turns them into images, by reading `.fa-name::before` rules from the
page's style sheets. Font Awesome 6 does not write such rules (it sets each
icon through a CSS variable), so the module adds them for every icon, with the
icon that `fa fa-name` markup draws. They are generated from the bundled Font
Awesome by `scripts/build_editor_css.py`: run it again after updating Font
Awesome.
