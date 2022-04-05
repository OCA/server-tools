You can add a minimum number of recipients on a ``ir.mail_server`` record (new field
in form view).

Then, when you send a mass mailing, if no mail server is specified on it,
Odoo will search for the first mail server that fits the condition, and use it.
As an example, consider that you define the following servers, in this order:

* Server A, minimum number of recipients : 10000;
* Server B, minimum number of recipients : 1000;
* Server C, minimum number of recipients : 100;
* Server D, minimum number of recipients : 10;
* Server E, minimum number of recipients : 0 (default value)

If you don't specify a mail server on the mass mailing, when sending it,
Odoo will compute the number of remaining recipients (using standard method
``_get_remaining_recipients()`` from mass mailing module). He will then use

* Server A, for a number of recipients at least 10000;
* Server B, for a number of recipients between 1000 and 9999;
* Server C, for a number of recipients between 100 and 999;
* Server D, for a number of recipients between 10 and 99;
* Server E, for a number of recipients less than 10.
