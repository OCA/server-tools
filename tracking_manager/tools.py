# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def format_m2m(records):
    if records:
        return "; ".join(records.mapped("display_name"))
    return ""
