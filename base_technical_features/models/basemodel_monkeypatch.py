# -*- coding: utf-8 -*-
# © 2016 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models


class BaseModelMonkeyPatch(models.AbstractModel):
    _name = 'basemodel.monkeypatch'

    def _register_hook(self):
        if not hasattr(
                models.BaseModel, 'base_technical_features_user_has_groups'):

            models.BaseModel.base_technical_features_user_has_groups = (
                models.BaseModel.user_has_groups)

            def user_has_groups(self, groups):
                """ Return True for users in the technical features group when
                membership of the original group is checked, even if debug mode
                is not enabled.
                """
                if ('base.group_no_one' in groups.split(',') and
                    self.env.user.has_group(
                        'base_technical_features.group_technical_features')):
                    return True
                return self.base_technical_features_user_has_groups(groups)

            models.BaseModel.user_has_groups = user_has_groups

        return super(BaseModelMonkeyPatch, self)._register_hook()
