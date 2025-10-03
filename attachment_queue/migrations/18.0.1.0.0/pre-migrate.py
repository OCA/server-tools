#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    xml_spec = [
        (
            "attachment_queue.view_attachment_queue_tree",
            "attachment_queue.view_attachment_queue_list",
        ),
        (
            "attachment_queue.act_open_attachment_que_view_tree",
            "attachment_queue.act_open_attachment_que_view_list",
        ),
    ]
    openupgrade.rename_xmlids(env.cr, xml_spec)
