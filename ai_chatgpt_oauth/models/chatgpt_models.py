# Copyright 2026 Mayur Bechara <becharamayur49@gmail.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).


def get_chatgpt_models(env):
    """Retrieve active ChatGPT models dynamically from the database."""
    try:
        model_records = env["ai.chatgpt.model"].sudo().search(
            [("active", "=", True)],
            order="sequence, id",
        )
        if model_records:
            return [(m.code, m.name) for m in model_records]
    except Exception:
        pass
    return []


def get_chatgpt_model_ids(env):
    """Return a set of valid active ChatGPT model identifiers."""
    models = get_chatgpt_models(env)
    return {model_id for model_id, _label in models}
