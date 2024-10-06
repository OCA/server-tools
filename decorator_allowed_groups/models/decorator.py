# Copyright (C) 2021-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api
from odoo.exceptions import AccessError


def allowed_groups(*group_xml_ids):
    """ Return a decorator that specifies group(s)
        to which the user must belong in order to perform
        this function.
        - if the user does not belong to any group,
        an AccessError will be raised if the function is called.
        - Also in the generated views, the according button
        will be hidden if the user doesn't belong to the group(s).

            @api.allowed_groups(
                "purchase.group_purchase_manager",
                "sale.group_sale_manager"
            )
            def my_secure_action(self):
                pass
    """

    def decorator(method):

        def secure_method(*args, **kwargs):

            _self = args[0]
            _final_method = getattr(_self, method.__name__)
            _group_xml_ids = getattr(_final_method, "_allowed_groups", [])

            # Check if current user is member of correct groups
            if _self.user_has_groups(','.join(_group_xml_ids)):
                # If it's OK, return the original method
                return method(*args, **kwargs)
            else:
                # If it's KO, raise an error.
                # We raise a technical message (with function name
                # and xml_ids of the groups, because this message
                # will be raised only in XML-RPC call.
                raise AccessError(_(
                    "To execute the function '%s', you should be member"
                    " of one of the following groups:\n '%s'") % (
                        method.__name__,
                        ', '.join(_group_xml_ids)
                    ))
        setattr(secure_method, "_allowed_groups", group_xml_ids)
        return secure_method

    return decorator


api.allowed_groups = allowed_groups
