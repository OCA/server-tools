# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from .patches import patch_load_modules


def post_load():
    patch_load_modules()
