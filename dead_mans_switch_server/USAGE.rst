Install `dead_mans_switch_client` on a customer instance and configure it as
described in that module's documentation. The clients will register themselves
with the server automatically. They will show up with their database uuid,
you'll have to assign a human readable description yourself.

At this point, you can assign a customer to this client instance for reporting
purposes, and, more important, add followers to the instance. They will be
notified in case the instance doesn't check back in time. Notification are only
turned on for instances in state 'active', instances in states 'new' or
'suspended' will be ignored.

You'll find the instances' current state at Dashboards/Customer instances.
