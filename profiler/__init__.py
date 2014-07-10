import controllers  # noqa
from cProfile import Profile


def patch_openerp():
    """Modify OpenERP/Odoo entry points so that profile can record.

    Odoo is a multi-threaded program. Therefore, the :data:`profile` object
    needs to be enabled/disabled each in each thread to capture all the
    execution.

    For instance, OpenERP 7 spawns a new thread for each request.
    """
    from openerp.addons.web.http import JsonRequest
    from .core import profiling
    orig_dispatch = JsonRequest.dispatch

    def dispatch(*args, **kwargs):
        with profiling():
            return orig_dispatch(*args, **kwargs)
    JsonRequest.dispatch = dispatch


def create_profile():
    """Create the global, shared profile object."""
    from . import core
    core.profile = Profile()


def post_load():
    create_profile()
    patch_openerp()
