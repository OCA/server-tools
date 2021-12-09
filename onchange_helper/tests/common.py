# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def setup_test_model(env, model_clses):
    for model_cls in model_clses:
        model_cls._build_model(env.registry, env.cr)

    env.registry.setup_models(env.cr)
    env.registry.init_models(
        env.cr,
        [model_cls._name for model_cls in model_clses],
        dict(env.context, update_custom_fields=True),
    )


def cleanup_test_model(env, model_clses):
    for model_cls in model_clses:
        env.registry.models.pop(model_cls._name, None)
        for model_classes in type(model_cls).module_to_models.values():
            if model_cls in model_classes:
                model_classes.remove(model_cls)

        for model in env:
            Model = env[model]

            if model_cls._name in Model._inherit_children:
                Model._inherit_children.remove(model_cls._name)

            if model_cls._name in Model._inherits_children:
                Model._inherits_children.remove(model_cls._name)
