# -*- coding: utf-8 -*-
from openerp.models import BaseModel

BaseModel.base_technical_features_user_has_groups = BaseModel.user_has_groups


def user_has_groups(self, cr, uid, groups, context=None):
    """ Return True for users in the technical features group when membership
    of this group is checked, even if debug mode is not enabled.
    """
    if ('base.group_no_one' in groups.split(',') and
            self.pool['res.users'].has_group(
                cr, uid, 'base_technical_features.group_technical_features')):
        return True
    return self.base_technical_features_user_has_groups(
        cr, uid, groups, context=context)

BaseModel.user_has_groups = user_has_groups
