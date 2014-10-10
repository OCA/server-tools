from openerp.osv import orm
from openerp.osv import osv
from openerp.tools.translate import _

__all__ = ['BaseModelMetaclassMixin']


def get_overrides():
    overrides = {}

    def add_override(func):
        overrides[func.func_name] = func

    @add_override
    def copy(cls, cr, uid, rec_id, default=None, context=None):
        # Raise by default. This method should be implemented to work.

        raise osv.except_osv(
            _(u"Warning"),
            _(u"Copy is not supported for this item.")
        )

    for func_name, func in overrides.iteritems():
        yield func_name, func


class BaseModelMetaclassMixin(orm.MetaModel):
    def __init__(cls, name, bases, nmspc):
        super(BaseModelMetaclassMixin, cls).__init__(name, bases, nmspc)

        for func_name, func in get_overrides():
            if not func_name in nmspc:
                setattr(cls, func_name, func)
