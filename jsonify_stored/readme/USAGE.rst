In some cases, odoo can complain about the db component not
being ready during the `jsonified_data` compute.
If so, copy the `pre_init_hook` and add it to your module where
a model inherits from `jsonify.stored.mixin`.
