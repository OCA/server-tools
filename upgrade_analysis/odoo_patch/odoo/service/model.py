from odoo.models import BaseModel


def _new_get_public_method(model, name):
    """Get the public unbound method from a model.
    When the method does not exist or is inaccessible, raise appropriate errors.
    Accessible methods are public (in sense that python defined it:
    not prefixed with "_") and are not decorated with `@api.private`.
    """
    assert isinstance(model, BaseModel), f"{model!r} is not a BaseModel for {name}"
    cls = type(model)
    method = getattr(cls, name, None)
    if not callable(method):
        raise AttributeError(
            f"The method '{model._name}.{name}' does not exist"
        )  # noqa: TRY004
    for mro_cls in cls.mro():
        cla_method = getattr(mro_cls, name, None)
        if not cla_method:
            continue
        # begin patch
        # if name.startswith('_') or getattr(cla_method, '_api_private', False):
        #    raise AccessError(
        #        f"Private methods (such as '{model._name}.{name}') cannot be called remotely."
        #    )  # pylint: disable=missing-gettext
        # end patch
    return method


# flake8: noqa: E402
import odoo.service.model

_new_get_public_method._original_method = odoo.service.model.get_public_method
odoo.service.model.get_public_method = _new_get_public_method
