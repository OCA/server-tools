.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Image URLs from HTML field
==========================

This module includes a method that extracts image URLs from any chunk of HTML,
in appearing order.

Usage
=====

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

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0

Known issues / Roadmap
======================

* The regexp to find the URL could be better.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Jairo Llopis <yajo.sk8@gmail.com>
* Vicent Cubells <vicent.cubells@tecnativa.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
