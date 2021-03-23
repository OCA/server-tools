import logging

_logger = logging.getLogger(__name__)


class OdooPatch(object):
    """Simple mechanism to apply a collection of monkeypatches using a
    context manager.

    Classes can register their monkeypatches by inheriting from this class.
    They need to define a `target` member, referring to the object or module
    that needs to be patched, and a list `method_names`. They also need to
    redefine those methods under the same name.

    The original method is made available on the new method as
    `_original_method`.

    Example:

    ```
    from odoo import api
    from odoo.addons.some_module.models.my_model import MyModel

    class MyModelPatch(OdooPatch):
    target = MyModel
    method_names = ['do_something']

    @api.model
    def do_something(self):
        res = MyModelPatch.do_something._original_method()
        ...
        return res
    ```

    Usage:

    ```
    with OdooPatch():
        do_something()
    ```
    """

    def __enter__(self):
        for cls in OdooPatch.__subclasses__():
            for method_name in cls.method_names:
                method = getattr(cls, method_name)
                method._original_method = getattr(cls.target, method_name)
                setattr(cls.target, method_name, method)

    def __exit__(self, exc_type, exc_value, tb):
        for cls in OdooPatch.__subclasses__():
            for method_name in cls.method_names:
                method = getattr(cls.target, method_name)
                if hasattr(method, "_original_method"):
                    setattr(cls.target, method_name, method._original_method)
                else:
                    _logger.warning(
                        "_original_method not found on method %s of class %s",
                        method_name,
                        cls.target,
                    )
