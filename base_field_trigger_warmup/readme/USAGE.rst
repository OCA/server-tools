There is nothing to do: installing the module is enough.

At the end of each registry load the module logs, at INFO level, how many
trigger trees it built and how long it took::

    INFO odoo.addons.base_field_trigger_warmup: Warmed up 24868 field
    trigger trees in 6.52s

Use that line to decide whether the default scope is worth its boot cost, and
narrow it down with the system parameter described in the configuration section
if it is not.
