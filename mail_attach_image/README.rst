.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=================
Mail attach image
=================

This module extends of module base and allows attach an image on email from the
base64 encoding.


Installation
============

To install this module, you need to:

- Not special pre-installation is required, just install as a regular Odoo
  module:

  - Go to ``Settings > Module list`` search for the current name and click in
    ``Install`` button.


Usage
=====

To use this module, you need add in email template the image base64 code,
as follow:

``<img src"data:image/png;base64,Base64code"/>``

The result is an email with the image attach:

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/mail_attach_image_eg1.png
    :align: center
    :width: 800

For further information, please visit:

* https://www.odoo.com/forum/help-1


Credits
=======


Contributors
------------


* Ivan Yelizariev <yelizariev@it-projects.info>
* Moises López <moylop260@vauxoo.com>
* Yennifer Santiago <yennifer@vauxoo.com>
* Vauxoo <info@vauxoo.com>


Maintainer
----------


.. image:: https://odoo-community.org/logo.png
    :alt: Odoo Community Association
    :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
