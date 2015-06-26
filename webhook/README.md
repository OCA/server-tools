Webhook
---------------

Module to receive [global webhooks](https://es.wikipedia.org/wiki/Webhook) events.
This module create dummy method to process events you will need create a new module to add your logic to process the events.

Your new module need have a inherit to `webhook` class and add override methods to work with your custom `webhook` module.

Method override `set_driver_remote_address` - Update dict `self.env.webhook_driver_address` key equal to name of your webhook consumer and value with list of all ip or subnet address (with `ip/integer`) owned by your webhook consumer.
Example with github:
```python
@api.one
def set_driver_remote_address(self):
    super(Webhook, self).set_driver_remote_address()
    self.env.webhook_driver_address.update({
        'github': ['192.30.252.0/22'] # https://help.github.com/articles/what-ip-addresses-does-github-use-that-i-should-whitelist/#current-ip-addresses
    })
```

Method override `set_event` - Update your variable `self.env.webhook_event` with logic to get event from request of your webhook consumer.
Example with github:
```python
@api.one
def set_event(self):
    super(Webhook, self).set_event()
    if not self.env.webhook_event and self.env.webhook_driver_name == 'github':
        self.env.webhook_event = self.env.request.httprequest.headers.get('X-Github-Event')
```


Add new methods named `"run_webhook_" + consumer_name + "_" + consumer_event` auto invoke in each webhook request.
Example with githup:
```python
@api.one
def run_webhook_github_push(self):
    # logic to run webhook event called "push" of "github"
    sys.stdout.write("Push event in: %s/%s\n" % (
        self.env.request.jsonrequest['repository']['owner']['name'],
        self.env.request.jsonrequest['repository']['name']
    ))
```

You can access to full request webhook data in variable `self.env.request`

Complete example with github:
```python
NAME_OF_YOUR_WEBHOOK_CONSUMER='github'
IP_OR_SUBNET_YOUR_WEBHOOK = ['192.30.252.0/22'] # https://help.github.com/articles/what-ip-addresses-does-github-use-that-i-should-whitelist/#current-ip-addresses

class Webhook(models.Model):
    _inherit = 'webhook'

    @api.one
    def set_driver_remote_address(self):
        super(Webhook, self).set_driver_remote_address()
        self.env.webhook_driver_address.update({
            NAME_OF_YOUR_WEBHOOK_CONSUMER: IP_OR_SUBNET_YOUR_WEBHOOK
        })

    @api.one
    def set_event(self):
        super(Webhook, self).set_event()
        if not self.env.webhook_event and \
                self.env.webhook_driver_name == NAME_OF_YOUR_WEBHOOK_CONSUMER:
            self.env.webhook_event = self.env.request.httprequest.headers.get('X-Github-Event')

    @api.one
    def run_webhook_github_push(self):
        # logic to run webhook event called "push" of "github"
        sys.stdout.write("Push event in: %s/%s\n" % (
            self.env.request.jsonrequest['repository']['owner']['name'],
            self.env.request.jsonrequest['repository']['name']
        ))
```
