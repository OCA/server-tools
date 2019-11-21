Set the implementation to "Standard" in all your current Sequences
(ir.sequence) and all new sequences are created as "Standard" by default
instead of "No Gap" implementation.

What's the problem with "No Gap" Sequence Implementations
=========================================================

"No Gap" is the default value of sequences in Odoo. However, this kind of
sequences cause more locks and can turn a database slow.

Taking as example an invoice, if you assign an invoice number to one record,
but it sill not finish the process, this process must end in order to another
invoice could assign a new number and there was no gaps between the invoice
numbers. It seems to be good at first sight. But the problem starts when there
is a chained process.

Imagine that there is one user that executes a process that produces 100
invoices and these at the same time produces 100 journal entries that also use
a consecutive (no gap) sequence. And also those invoices are sent to sign with
and external institution (that could take 2 seconds in giving a response
because of internet latency or server load), and maybe they made another
calculations that makes them to take 5 seconds more for each invoice, and all
this is chained to one single transaction. This means that for 8.5 minutes
anybody else could confirm invoices, neither journal entries of the involved
journals.

Now, think there is 20 users that have to execute a similar process. The
problem turns exponential. If another user comes to make an operation with the
same jornal it will thrown a concurrency failure.

You can mitigate it if you segment each transaction and don't chain them. It
means, making commit for each invoice or process. It reduces the
probability that there is a concurrency error or a lock wait. However, it still
not solve it completely.

Why to use Sequences with "Standard" Implementation
===================================================

If you use the standard sequence of PosgreSQL, it doesn't lock because at the
moment the request is done, the next sequence number it is changed in an
isolated transaction, and it have not to wait the other transaction to end.
However, if the transaction produces a rollback, this sequence isn't reverted,
it means, it's lost. It may be not not serious because when you cancel or
remove records that number is lost too.

What this module does
=====================

To eliminate completely that concurrency/slowness problem, this module changes
all the sequences (ir.sequence) implementation from "No Gap" to "Standard" with
the awareness that it will skip numbers. In the majority of database models
and many users projects there is no problem with that jump occurs.
