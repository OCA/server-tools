This module allow user to add optional sequences to some document model.
On which sequence is used, is based on domain matching with document
values (and original sequence will be bypassed).

For example, it is now possible to,

- Avoid using Odoo automatic sequence on invoice and vendor bill with
  old style sequence.
- Customer payment and vendor payment to run on different sequence.
- Assign different sales order sequence based on customer region.

This is a base module and does nothing by itself. Following are modules
that will allow managing sequence options for each type of documents,
I.e.,

- Purchase Order: purchase_sequence_option
- Invoice / Bill / Refund / Payment: account_sequence_option
- Others: create a new module with few lines of code
