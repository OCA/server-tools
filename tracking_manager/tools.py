# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def format_m2m(records):
    # In some cases (I.E. account_asset/models/account_asset.py), _message_track
    # is called with a dict of None values as initial_values.
    # As a result, create_tracking_values would be called with None as initial_value
    # and this format_m2m would be called with None as an argument.
    # In such case, return "None"
    if records:
        return "; ".join(records.mapped("display_name"))
    return ""
