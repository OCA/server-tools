How to
======
::

    # In an Openerp Module:
    from base_model_metaclass_mixin import BaseModelMetaclassMixin


    class oetest(osv.Model):
        __metaclass__ = BaseModelMetaclassMixin

    # Functions defined in BaseModelMetaclassMixin will be automatically added if they are not
    # implemented in the osv.Model class

