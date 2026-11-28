# Copyright 2016-2020 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    env["letsencrypt"]._get_key("account.key")
