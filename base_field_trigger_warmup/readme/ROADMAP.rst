The module relies on ``Registry.get_field_trigger_tree``, which is private ORM
API. It is called defensively: if a future Odoo version renames or removes it,
the module logs the fact and does nothing instead of breaking the registry
load. Porting to a new version should start by checking that method.

Warming up the trees hides the symptom of a wide compute graph. When the first
request of a worker is slow enough to need this module, it is also worth
looking at whether the graph itself can be reduced.
