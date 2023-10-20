# Copyright 2021 Ecosoft (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import api, models


class BaseModel(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        """
        This function convert value to multi value

        Normally Odoo search
        ------------------------------------------------
        [['name', 'ilike', '{P00001 P00002 P00003}']]

        Convert to multi value
        ------------------------------------------------
        ['|', '|', '|', ['name', 'ilike', '{P00001 P00002 P00003}'],
            ['name', 'ilike', 'P00001'],
            ['name', 'ilike', 'P00002'],
            ['name', 'ilike', 'P00003']]
        """
        new_arg = []
        for arg in args:
            # search value is {} for convert to multi value
            match = re.search("{.+}", str(arg))
            if match and (isinstance(arg, list) or isinstance(arg, tuple)):
                # find value in {} and convert to multi value
                list_parcel_number = re.findall(r"(\w+)", arg[2])
                x = [arg]
                for parcel in list_parcel_number:
                    x.append([arg[0], "ilike", parcel])
                    x.insert(0, "|")
                new_arg.extend(x)
            else:
                new_arg.append(arg)
        return super()._search(new_arg, offset, limit, order, count, access_rights_uid)
