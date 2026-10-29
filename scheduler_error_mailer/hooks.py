# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    env["ir.cron"].with_context(active_test=False).search([]).write(
        {
            "email_template_id": env.ref(
                "scheduler_error_mailer.scheduler_error_mailer"
            ).id
        }
    )
