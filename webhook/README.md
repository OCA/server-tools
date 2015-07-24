Webhook
---------------

Module to receive [global webhooks](https://en.wikipedia.org/wiki/Webhook) events.
This module invoke methods to process webhook events.
You will need create a new module to add your logic to process the events with methods called:
`def run_CONSUMER_EVENT*`
Example with gihub consumer and push event.
```python
@api.one
def run_github_push_task(self):
    # You will have all request data in 
    # variable: self.env.request
    pass
```

Where CONSUMER is the name of you webhook consumer. e.g. github (Extract from field `name` of `webhook` model)
Where EVENT is the name of the event from webhook `request` data.
Where `*` is your particular method to process this event.

To configure a new webhook you need add all ip or subnet address (with `ip/integer`) owned by your webhook consumer in webhook.address model as data.

Example with github:
```xml
<!--webhook github data of remote address-->
<record model="webhook.address" id="webhook_address_github">
    <field name="name">192.30.252.0/22</field>
    <field name="webhook_id" ref="webhook_github"/>
</record>
```

You need to add a python code to extract event name from webhook request info into `python_code_get_event` field of webhook model.
You can get all full data of request webhook from variable `request`
Example with github:
```xml
<!--webhook github data-->
<record model="webhook" id="webhook_github">
    <field name="name">github</field>
    <field name="python_code_get_event">request.httprequest.headers.get('X-Github-Event')</field>
</record>
```

Full example of create a new webhook configuration data.
```xml
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
```

External Dependecies
---------------
Install python package ipaddress
You can use pip to install
`pip install ipaddress`

