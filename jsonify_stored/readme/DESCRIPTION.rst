This module provides a mixin to store some json-ified data
that depends on an export, such that its recomputation is guaranteed by the ORM.
Moreover the data can be recomputed asynchronously,
or computed on-demand if accessed explicitly.

When inheriting from this mixin, the `xml_id` should exist before the model init.
This means the export id cannot be in the module data; it should either be in a
module dependency, or created in a pre_init_hook
(it is fine to simply create the record and the `ir.model.data` in the hook
and then update it in the xml data, e.g. to let the lines in the data only).

There is a generic cron that can be used to recompute the data, which could be
removed in favour of model-specific ones, so as to control how many records when.
