#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    xml_spec = [
        (
            "attachment_synchronize.view_attachment_queue_tree",
            "attachment_synchronize.view_attachment_queue_list",
        ),
        (
            "attachment_synchronize.view_attachment_task_tree",
            "attachment_synchronize.view_attachment_task_list",
        ),
    ]
    openupgrade.rename_xmlids(env.cr, xml_spec)
