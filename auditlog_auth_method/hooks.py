# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .rpc import patch_rpc_controller, patch_rpc_dispatch


def post_load_hook():
    patch_rpc_dispatch()
    patch_rpc_controller()
