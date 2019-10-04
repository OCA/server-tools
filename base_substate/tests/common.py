# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def setup_test_model(env, model_clses):
    for model_cls in model_clses:
        model_cls._build_model(env.registry, env.cr)

    env.registry.setup_models(env.cr)
    env.registry.init_models(
        env.cr, [model_cls._name for model_cls in model_clses],
        dict(env.context, update_custom_fields=True)
    )
    for model_cls in model_clses:
        model = env[model_cls._name]
        # setup_models():
        model._prepare_setup()
        model._setup_base()
        model._setup_fields()
        # init_models():
        model._setup_complete()
        model._auto_init()
        model.init()
        while env.registry._post_init_queue:
            func = env.registry._post_init_queue.popleft()
            func()
