Webhook github
---------------

Module to receive [github webhooks](https://developer.github.com/webhooks/) events.
This module create dummy method to [events method of github](https://developer.github.com/webhooks/#events) you will need create a new module to add your logic to events.

Your new module need have a inherit to webhook class and add override methods to work with your custom webhook module.

With next structure:
```python
@api.one
def run_webhook_github_push(self):
  # logic to run webhook event called "push" of github
```

You can access to full request webhook data in variable `self.env.request`

Example with `push` event of github
```python
@api.one
def run_webhook_github_push(self):
    # logic to run webhook event called "push" of "github"
    sys.stdout.write("Push event in: %s/%s\n" % (
        self.env.request.jsonrequest['repository']['owner']['name'],
        self.env.request.jsonrequest['repository']['name']
    ))
```
