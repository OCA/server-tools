# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import importlib
import inspect
import logging

from .decorator import profiled

_logger = logging.getLogger(__name__)

_PATCHED = {}


def _safe_import(module_path):
    try:
        return importlib.import_module(module_path)
    except Exception as exc:
        _logger.warning("Unable to import %s: %s", module_path, exc)
        return None


def _resolve_target(path):
    if not path or "." not in path:
        raise ValueError("Invalid python path")

    parts = path.split(".")
    if len(parts) < 2:
        raise ValueError("Invalid python path")

    module_path = ".".join(parts[:-1])
    module = _safe_import(module_path)
    if module and hasattr(module, parts[-1]):
        return {
            "owner": module,
            "attr": parts[-1],
            "descriptor": getattr(module, parts[-1]),
            "restore_action": "set",
        }

    if len(parts) < 3:
        raise ValueError("Invalid python path")

    module_path = ".".join(parts[:-2])
    class_name = parts[-2]
    attr = parts[-1]
    module = _safe_import(module_path)
    if not module:
        raise ValueError("Module could not be imported")

    owner = getattr(module, class_name, None)
    if owner is None or not inspect.isclass(owner):
        raise ValueError("Class not found on module")

    if not hasattr(owner, attr):
        raise ValueError("Attribute not found on class")

    raw = owner.__dict__.get(attr)
    restore_action = "set" if raw is not None else "delete"
    descriptor = raw if raw is not None else getattr(owner, attr)

    return {
        "owner": owner,
        "attr": attr,
        "descriptor": descriptor,
        "restore_action": restore_action,
    }


def validate_path(path):
    target = _resolve_target(path)
    wrapped = _wrap_descriptor(target["descriptor"], 0.0)
    if wrapped is None:
        raise ValueError("Target is not callable")
    return True


def _wrap_descriptor(descriptor, sample_rate):
    if isinstance(descriptor, staticmethod):
        wrapped = _wrap_callable(descriptor.__func__, sample_rate)
        return staticmethod(wrapped)
    if isinstance(descriptor, classmethod):
        wrapped = _wrap_callable(descriptor.__func__, sample_rate)
        return classmethod(wrapped)
    if inspect.isfunction(descriptor):
        return _wrap_callable(descriptor, sample_rate)
    if inspect.ismethod(descriptor):
        return _wrap_callable(descriptor.__func__, sample_rate)
    if callable(descriptor):
        return _wrap_callable(descriptor, sample_rate)
    return None


def _wrap_callable(func, sample_rate):
    if getattr(func, "_profiled_wrapped", False):
        return func

    wrapped = profiled(sample_rate)(func)
    wrapped._profiled_wrapped = True
    wrapped._profiled_origin = func
    return wrapped


def patch_path(path, sample_rate):
    if path in _PATCHED:
        if _PATCHED[path]["sample_rate"] == sample_rate:
            return False
        unpatch_path(path)

    target = _resolve_target(path)
    wrapped = _wrap_descriptor(target["descriptor"], sample_rate)
    if wrapped is None:
        _logger.warning("Target %s is not callable", path)
        return False

    setattr(target["owner"], target["attr"], wrapped)
    _PATCHED[path] = {
        "owner": target["owner"],
        "attr": target["attr"],
        "original": target["descriptor"],
        "restore_action": target["restore_action"],
        "sample_rate": sample_rate,
    }
    _logger.info("Profiled decorator applied on %s", path)
    return True


def unpatch_path(path):
    info = _PATCHED.pop(path, None)
    if not info:
        return False

    if info["restore_action"] == "delete":
        try:
            delattr(info["owner"], info["attr"])
        except AttributeError as exc:
            _logger.error(
                "Unable to remove profile patch for %s: attribute not found",
                path,
                exc,
                _info=True,
            )
            pass
    else:
        setattr(info["owner"], info["attr"], info["original"])

    _logger.info("Profiled decorator removed from %s", path)
    return True


def patch_active_records(records):
    desired = {rec.python_path: rec for rec in records}

    for path in list(_PATCHED):
        if path not in desired:
            unpatch_path(path)

    for path, rec in desired.items():
        try:
            patch_path(path, rec.sample_rate)
        except Exception as exc:
            _logger.warning("Unable to patch %s: %s", path, exc)
