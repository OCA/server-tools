from odoo.tools.convert import xml_import

from .common import disable_changeset

orig_xml_import_get_env = xml_import.get_env


def post_load():
    """
    Monkey patch the loading of XML module data.

    Otherwise, existing rules may break the installation of other modules.
    """

    def get_env(self, node, eval_context=None):
        env = orig_xml_import_get_env(self, node, eval_context=eval_context)
        if "__no_changeset" not in env.context:
            env = env(context=dict(**env.context, __no_changeset=disable_changeset))
        return env

    xml_import.get_env = get_env
