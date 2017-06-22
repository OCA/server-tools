Go to get correct sender information on messages from e-mail service providers
which have implemented DMARC policies, to group services like Google Groups.
In this case, the original sender should be read based on ‘X-Original-From’
value of the email header, instead of the ‘From’ value which is taken by Odoo.
