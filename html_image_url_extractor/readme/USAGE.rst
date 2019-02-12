This module just adds a technical utility, but nothing for the end user.

If you are a developer and need this utility for your module, see these
examples and read the docs inside the code.

Python example::

    @api.multi
    def some_method(self):
        # Get images from an HTML field
        imgs = self.env["ir.fields.converter"].imgs_from_html(self.html_field)
        for url in imgs:
            # Do stuff with those URLs
            pass

QWeb example::

    <!-- Extract first image from a blog post -->
    <t t-foreach="env['ir.fields.converter']
                  .imgs_from_html(blog_post.content, 1)"
       t-as="url">
        <img t-att-href="url"/>
    </t>
