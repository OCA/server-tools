Whenever a new request is processed by Odoo, this statement is evaluated:
`random.random() < 0.001` [1_]

.. _1: https://github.com/odoo/odoo/blob/a0a11fd5e2d78e5fc0d1503275adade570fe0d42/odoo/http.py#L1192

1 time out of 1000 in average, it will return `True` and trigger the
Garbage Collection of sessions: sessions that have
not been active for more than 1 week will be deleted [2_]

.. _2: https://github.com/odoo/odoo/blob/a0a11fd5e2d78e5fc0d1503275adade570fe0d42/odoo/http.py#L1193

This random approach can become a problem in some contexts.

On a highly visited Odoo website, many sessions will be created.
Going through all of them will take some time, especially on a slow/loaded FS.
The Garbage Collection happening randomly, your users will report
you cases of Odoo being randomly slow on random actions. They won't be able
to reproduce these cases and you won't be able to trace them in your
odoo logs neither, because calls' response time doesn't include the time Odoo
spent on the Garbage Collection.

Moreover, on a heavily loaded server, better be in a position to
control when does the Garbage Collection happen. One might want to run it once
per night only for example.

That's why we created this module:

- to disable the default random Garbage Collection
- to enable administrators to replace it by a deterministic approach:

  - either by using the included Scheduled Action;
  - or by calling the added public method
    `ir.autovacuum:gc_sessions()` remotely
