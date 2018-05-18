# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError


def migrate(cr, version):
    # Fix typo across DB
    cr.execute(
        """ UPDATE res_authentication_attempt
            SET result = 'successful'
            WHERE result = 'successfull'""",
    )
    # Store whitelist IPs in new format
    cr.execute(
        """ SELECT remote
            FROM res_banned_remote
            WHERE active IS FALSE""",
    )
    remotes = {record[0] for record in cr.fetchall()}
    try:
        with cr.savepoint():
            cr.execute(
                "INSERT INTO ir_config_parameter (key, value) VALUES (%s, %s)",
                (
                    "auth_brute_force.whitelist_remotes",
                    ",".join(remotes),
                ),
            )
    except IntegrityError:
        # Parameter already exists
        cr.execute(
            "SELECT value FROM ir_config_parameter WHERE key = %s",
            ("auth_brute_force.whitelist_remotes",)
        )
        current = set(cr.fetchall()[0][0].split(","))
        cr.execute(
            "UPDATE ir_config_parameter SET value = %s WHERE key = %s",
            (",".join(current | remotes),
             "auth_brute_force.whitelist_remotes"),
        )
    # Update the configured IP limit parameter
    cr.execute(
        "UPDATE ir_config_parameter SET key = %s WHERE key = %s",
        (
            "auth_brute_force.whitelist_remotes",
            "auth_brute_force.max_by_ip",
        )
    )
