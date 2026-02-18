To use this module, follow these steps:

1. Create one or more sequence templates and define the desired prefix and
   suffix, with company placeholders if desired. You can use placeholders like:
   * `%(company_id.id)s`
   * `%(company_id.name)s`
   * `%(company_id.vat)s`
2. Select the templates you want to use.
3. Trigger the server action that opens the wizard to generate sequences for
   companies.
4. In the wizard, select the target companies.
5. Confirm to generate the sequences.

The wizard will:
- Read the required company fields used in the templates.
- Validate that those fields exist and are not empty.
- Create one `ir.sequence` per selected company and template with the resolved
  values.

