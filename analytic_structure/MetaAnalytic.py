from openerp.osv import fields
from openerp.tools import config
from openerp.addons.oemetasl import OEMetaSL


class MetaAnalytic(OEMetaSL):
    """Generate analytic fields on a model, applying the required changes on
    its class attributes and methods.
    """

    def __new__(cls, name, bases, nmspc):

        # Analytic fields should be defined in the _analytic attribute.
        analytic = nmspc.get('_analytic', False)
        if not analytic:
            return super(MetaAnalytic, cls).__new__(cls, name, bases, nmspc)

        # If it uses a shortcut, convert it into a prefix -> model mapping.
        if analytic is True:
            orm_model_name = nmspc.get('_name', False)
            if orm_model_name is False:
                orm_model_name = nmspc.get('_inherit')
            analytic = {'a': orm_model_name}
        elif isinstance(analytic, basestring):
            analytic = {'a': analytic}
        nmspc['_analytic'] = analytic

        size = int(config.get_misc('analytic', 'analytic_size', 5))
        columns = nmspc.get('_columns', False)
        if columns is False:
            columns = {}
            nmspc['_columns'] = columns

        # Generate the analytic fields directly into the _columns attribute.
        for prefix, model_name in analytic.iteritems():
            for n in xrange(1, size + 1):
                col_name = '{pfx}{n}_id'.format(pfx=prefix, n=n)
                domain_field = 'nd_id.ns{n}_id.model_name'.format(n=n)
                columns[col_name] = fields.many2one(
                    'analytic.code',
                    u"Analysis Code 1",
                    domain=[(domain_field, '=', model_name)],
                    track_visibility='onchange',
                )

        # In order to preserve inheritance, possible overrides, and OEMetaSL's
        # expected behavior, work on a new class that inherits the given bases,
        # then make our model class inherit from this class.
        superclass_name = '_{name}_SuperAnalytic'.format(name=name)
        # Set _register to False in order to prevent its instantiation.
        superclass = type(superclass_name, bases, {'_register': False})

        def fields_get(
            self, cr, uid, allfields=None, context=None, write_access=True
        ):
            """Override this method to rename analytic fields."""

            res = super(superclass, self).fields_get(
                cr, uid, allfields=allfields, context=context,
                write_access=write_access
            )

            analytic_osv = self.pool.get('analytic.structure')

            for prefix, model_name in analytic.iteritems():
                res = analytic_osv.analytic_fields_get(
                    cr, uid, model_name, res, prefix=prefix, context=context
                )

            return res

        def fields_view_get(
            self, cr, uid, view_id=None, view_type='form', context=None,
            toolbar=False, submenu=False
        ):
            """Override this method to hide unused analytic fields."""

            res = super(superclass, self).fields_view_get(
                cr, uid, view_id=view_id, view_type=view_type, context=context,
                toolbar=toolbar, submenu=submenu
            )

            analytic_osv = self.pool.get('analytic.structure')

            for prefix, model_name in analytic.iteritems():
                res = analytic_osv.analytic_fields_view_get(
                    cr, uid, model_name, res, prefix=prefix, context=context
                )

            return res

        setattr(superclass, 'fields_get', fields_get)
        setattr(superclass, 'fields_view_get', fields_view_get)
        new_bases = (superclass,)
        return super(MetaAnalytic, cls).__new__(cls, name, new_bases, nmspc)

    def __init__(self, name, bases, nmspc):
        return super(MetaAnalytic, self).__init__(name, bases, nmspc)
