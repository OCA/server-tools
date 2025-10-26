This module provides integration between `base_fontawesome` and Odoo's `web_editor` to ensure FontAwesome >= 6.7.2 icons are properly displayed in the web editor.

It patches the font icon detection system to work with FontAwesome >= 6.7.2 CSS structure and filters CSS rules to only process those containing the `--fa` variable.
