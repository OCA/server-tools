This module provides a wizard to generate company-specific sequences from
reusable sequence templates. It is designed for multi-company environments
where each company requires its own `ir.sequence` records but shares a common
configuration pattern. The wizard allows defining sequence templates that
include dynamic placeholders referencing company fields.

During generation, placeholders of the form `%(company_id.<field>)s` are
automatically replaced with the corresponding values from each company. Other
placeholders (for example `%(year)s`) are preserved and evaluated later by the
standard sequence engine. The module also validates that all referenced company
fields exist and checks that required company values are not empty.

