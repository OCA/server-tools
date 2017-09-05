# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models


_logger = logging.getLogger(__file__)


# TODO: this should be a helper module to cetralize the point of failure
# in case this introduces tacit bugs
class BasePatchModelsMixin(models.AbstractModel):
    """
    This is a mixin class meant to simplify working with patches
    on BaseModel or on abstract models like mail.thread.
    If you just change them, models created earlier will lack the
    attributes you add. Just inherit from this mixin, it will check
    which existing models need your changes and apply them.

    In your module, do something like

    class MailThread(models.AbstractModel):
        _name = 'mail.thread'
        _inherit = ['base.patch.models.mixin', 'mail.thread']

    in case you need to patch BaseModel, say

    class BaseModel(models.BaseModel):
        _name = 'my.unique.model.name'
        _inherit = 'base.patch.models.mixin'

    Your code will behave as if it was an inherited class of the class you pass
    in the second parameter to _base_patch_models.
    """
    _name = 'base.patch.models.mixin'

    def _base_patch_models(self, cr, our_class=None, parent_class=None):
        """iterate through existing models to apply our changes there if
        necessary"""
        if self._name == BasePatchModelsMixin._name:
            return
        my_bases = self.__class__.__bases__
        for i in range(max(len(my_bases) - 1, 0)):
            if my_bases[i]._name == BasePatchModelsMixin._name:
                our_class = my_bases[i - 1]
                parent_class = my_bases[i + 1]
        inherit = [self._inherit]\
            if isinstance(self._inherit, basestring) else self._inherit
        for i in range(len(my_bases) - 1, 0, -1):
            # this can be different from the above if our mixin is used
            # multiple times on the same model
            if my_bases[i]._name in inherit:
                parent_class = my_bases[i]
                break
        if self.__class__.__bases__[-1] == BasePatchModelsMixin\
                and not our_class or not parent_class:
            our_class = self.__class__.__bases__[-2]
            parent_class = models.BaseModel
        if not our_class or not parent_class:
            _logger.info(
                'Failed to autodetect own class or parent class for %s, '
                'ignoring', self._name)
            return

        for model_name, model_object in self.pool.models.iteritems():
            if not isinstance(model_object, parent_class):
                continue
            if isinstance(model_object, our_class):
                continue
            if not isinstance(model_object, models.Model):
                continue
            bases = list(model_object.__class__.__bases__)
            position = 1
            if parent_class == models.BaseModel:
                position = len(bases)
            else:
                for i in range(len(bases) - 1, position, -1):
                    if bases[i]._name in inherit:
                        position = i
                        break
            bases.insert(position, our_class)
            model_object.__class__.__bases__ = tuple(bases)

    def _register_hook(self, cr):
        self._base_patch_models(cr)
        for base in self.__class__.__bases__:
            if not hasattr(super(base, self), '_register_hook'):
                return
            if super(base, self)._register_hook != self._register_hook:
                return super(base, self)._register_hook.__func__(
                    super(base, self), cr)
