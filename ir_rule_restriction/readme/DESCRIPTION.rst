Right now, Odoo defines to types of record rules:
Global: All of them must have allow the action to be performed in order for
the operation a user is performing to succeed. Therefore, an AND is
performed in all of them.
Group-specific: Any of them can allow the action to be performed in order for
the operation a user is performing to succeed. Therefore, an OR is
performed in all of them.

Which means that if we have userA of groupA which global rules allow them to
perform actionA on modelA, there is no way for us to perform an operation of:
"Everyone but users of groupA should be able to do actionA on modelA"

We resolve this by giving the opportunity to Administrators to have a specific
rule have an AND operation performed on it.
