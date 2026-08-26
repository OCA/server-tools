This module just adds a technical utility, but nothing for the end user.

If you are a developer and need this utility for your module, see these
examples and read the docs inside the code.

Python example:

    def some_method(self):
        # Get truncated text from an HTML field. It will 40 words and 100
        # characters at most, and will have "..." appended at the end if it
        # gets truncated.
        truncated_text = self.env["ir.fields.converter"].text_from_html(
            self.html_field, 40, 100, "...")

QWeb example:

    <t t-esc="env['ir.fields.converter'].text_from_html(doc.html_field)"/>

[![Try me on Runbot](https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas)](https://runbot.odoo-community.org/runbot/149/11.0)
