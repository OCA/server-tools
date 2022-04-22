This is a technical module,
hence you should take care of extending your models w/ `jsonifier.stored.mixin`.

Your module should also provide a `base_jsonify` compatible exporter
by overriding `_jsonify_get_exporter`.

The cron "JSONify stored - Recompute data for all models"
will recompute data for all inheriting models.

Computations is delegated to queue jobs and by default each job will compute 5 records.
You can tweak this by passing `chunk_size` to `cron_update_json_data_for`.

If your model has a lang field, before jobs are created,
records will be grouped by language.

NOTE: if the model is already existing in your DB is recommended to use
`jsonifier_stored.hooks.add_jsonifier_column` function
to prevent Odoo to compute all data when you update your module.
