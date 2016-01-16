# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openerp import SUPERUSER_ID, models


_logger = logging.getLogger(__file__)


class BasePatchModelsMixin(models.AbstractModel):
    """This is a mixin class meant to simplify working with patches
    on BaseModel or on abstract models like mail.thread.
    If you just change them, models created earlier will lack the
    attributes you add. Just inherit from this mixin, it will check
    which existing models need your changes and apply them.
    
    In your module, do something like

    from openerp.addons.mail.mail_thread import mail_thread

    class MailThread(models.AbstractModel):
        _name = 'mail.thread'
        _inherit = ['base.patch.models.mixin', 'mail.thread']

        def _register_hook(self, cr):
            self._base_patch_models(cr, MailThread, mail_thread)
            return super(MailThread, self)._register_hook(cr)

    in case you need to patch BaseModel, say

    class AbstractModel(models.AbstractModel):
        _name = 'my.patch.model'
        _inherit = 'base.patch.models.mixin'

        def _register_hook(self, cr):
            self._base_patch_models(cr, AbstractModel, models.AbstractModel)
            return super(AbstractModel, self)._register_hook(cr)

    """
    _name = 'base.patch.models.mixin'

    def _base_patch_models(self, cr, our_class, parent_class):
        """iterate through existing models to apply our changes there if
        necessary"""
        rebuilt = []
        for model_name in self.pool:
            model_object = self.pool[model_name]
            if not isinstance(model_object, parent_class):
                continue
            if isinstance(model_object, our_class):
                continue
            bases = list(model_object.__class__.__bases__)
            class_dict = dict(model_object.__dict__)
            class_dict['_inherit'] = model_name
            class_dict['_name'] = model_name
            if our_class not in bases:
                position = 1
                if parent_class == models.BaseModel:
                    position = len(bases)
                bases.insert(position, our_class)
            new_model_class = type(model_name, tuple(bases),
                                   class_dict)
            new_model = new_model_class._build_model(self.pool, cr)
            self.pool.models[model_name] = new_model
            new_model._prepare_setup(cr, SUPERUSER_ID)
            new_model._setup_base(cr, SUPERUSER_ID, False)
            new_model._setup_fields(cr, SUPERUSER_ID)
            rebuilt.append(new_model)
        for model in rebuilt:
            model._setup_complete(cr, SUPERUSER_ID)
        return super(BasePatchModelsMixin, self)._register_hook(cr)
