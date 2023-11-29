from collections import defaultdict

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
            SELECT ir_model_id, res_groups_id
            FROM ir_model_group_readonly_rel_tmp;
        """,
    )
    data = env.cr.fetchall()
    grouped = defaultdict(list)
    for key, value in data:
        grouped[key].append(value)
    vals_list = [
        {"model_id": model_id, "group_ids": group_ids}
        for model_id, group_ids in grouped.items()
    ]
    env["model.readonly.restriction"].create(vals_list)
    openupgrade.logged_query(
        env.cr,
        """
            DROP TABLE ir_model_group_readonly_rel_tmp;
        """,
    )
