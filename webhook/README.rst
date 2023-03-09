.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======
Webhook
=======

Module to receive `webhook events <https://en.wikipedia.org/wiki/Webhook>`_.
This module invoke methods to process webhook events.

Configuration
=============

You will need create a new module to add your logic to process the events with methods called:
*def run_CONSUMER_EVENT\**

Example with gihub consumer and push event.

.. code-block:: python

    @api.one
    def run_github_push_task(self):
        # You will have all request data in 
        # variable: self.env.request
        pass


Where CONSUMER is the name of you webhook consumer. e.g. github (Extract from field *name* of *webhook* model)
Where EVENT is the name of the event from webhook *request* data.
Where *\** is your particular method to process this event.

To configure a new webhook you need add all ip or subnet address (with *ip/integer*) owned by your webhook consumer in webhook.address model as data.

Example with github:

.. code-block:: xml

    <!--webhook github data of remote address-->
    <record model="webhook.address" id="webhook_address_github">
        <field name="name">192.30.252.0/22</field>
        <field name="webhook_id" ref="webhook_github"/>
    </record>


You need to add a python code to extract event name from webhook request info into `python_code_get_event` field of webhook model.
You can get all full data of request webhook from variable `request`
Example with github:

.. code-block:: xml

    <!--webhook github data-->
    <record model="webhook" id="webhook_github">
        <field name="name">github</field>
        <field name="python_code_get_event">request.httprequest.headers.get('X-Github-Event')</field>
    </record>


Full example of create a new webhook configuration data.

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <openerp>
        <data>

            <!--webhook github data-->
            <record model="webhook" id="webhook_github">
                <field name="name">github</field>
                <field name="python_code_get_event">request.httprequest.headers.get('X-Github-Event')</field>
            </record>
            <!--webhook github data of remote address-->
            <record model="webhook.address" id="webhook_address_github">
                <field name="name">192.30.252.0/22</field>
                <field name="webhook_id" ref="webhook_github"/>
            </record>

        </data>
    </openerp>


.. figure:: path/to/local/image.png
   :alt: alternative description
   :width: 600 px

Usage
=====

To use this module, you need to:

#. Go to your customer webhook configuration from 3rd-party applications
   and use the odoo webhook url HOST/webhook/NAME_WEBHOOK

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Moisés López <moylop260@vauxoo.com>

Funders
-------

The development of this module has been financially supported by:

* Vauxoo

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
