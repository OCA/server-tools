from openerp.osv import fields
from openerp.tools import config
from openerp.addons.oemetasl import OEMetaSL
from openerp import SUPERUSER_ID


class AddMethod(object):
    """Utility decorator to add methods to an object or a class."""

    def __init__(self, obj):
        self.obj = obj

    def __call__(self, func):
        setattr(self.obj, func.func_name, func)
        return func


class MetaAnalytic(OEMetaSL):
    """Allow the model to use the classes of the analytic_structure module
    in a more streamlined way.

    The metaclass' behavior is specified by adding the following attributes:

    * _analytic: define the analytic structures to be used by the model.
    * _dimensions: bind an analytic dimension to the model.

    A description of the syntax expected for each attribute is available in
    the README file.

    Notes:
    * This metaclass may directly modify attributes that are used by OpenERP,
    specifically _columns and _inherits.
    * New superclasses are used to define or override methods, in order to
    avoid interacting with OEMetaSL or the model's own method (re)definitions.
    """

    def __new__(cls, name, bases, nmspc):

        analytic = nmspc.get('_analytic', False)
        dimension = nmspc.get('_dimension', False)

        columns = nmspc.get('_columns', None)
        if columns is None:
            columns = {}
            nmspc['_columns'] = columns

        orm_name = nmspc.get('_name', None)
        if orm_name is None:
            orm_name = nmspc.get('_inherit')

        # Analytic fields should be defined in the _analytic attribute.
        if analytic:
            bases = cls._setup_analytic_fields(
                analytic, columns, orm_name, name, bases, nmspc
            )

        # The bound dimension should be defined in the _dimension attribute.
        if dimension:
            bases = cls._setup_bound_dimension(
                dimension, columns, orm_name, name, bases, nmspc
            )

        return super(MetaAnalytic, cls).__new__(cls, name, bases, nmspc)

    def __init__(self, name, bases, nmspc):
        return super(MetaAnalytic, self).__init__(name, bases, nmspc)

    @classmethod
    def _setup_analytic_fields(
        cls, analytic, columns, orm_name, name, bases, nmspc
    ):
        """Generate analytic fields on the model."""

        # If _analytic uses a shortcut, convert it into a prefix-model mapping.
        if analytic is True:
            analytic = {'a': orm_name.replace('.', '_')}
        elif isinstance(analytic, basestring):
            analytic = {'a': analytic}
#        nmspc['_analytic'] = analytic

        size = int(config.get_misc('analytic', 'analytic_size', 5))

        # Generate the analytic fields directly into the _columns attribute.
        for prefix, model_name in analytic.iteritems():
            for n in xrange(1, size + 1):
                col_name = '{pfx}{n}_id'.format(pfx=prefix, n=n)
                domain_field = 'nd_id.ns{n}_id.model_name'.format(n=n)
                columns[col_name] = fields.many2one(
                    'analytic.code',
                    "Generated Analytic Field",
                    domain=[
                        (domain_field, '=', model_name),
                        ('child_ids', '=', False)
                    ],
                    track_visibility='onchange',
                )

        # In order to preserve inheritance, possible overrides, and OEMetaSL's
        # expected behavior, work on a new class that inherits the given bases,
        # then make our model class inherit from this class.
        superclass_name = '_{name}_SuperAnalytic'.format(name=name)
        # Set _register to False in order to prevent its instantiation.
        superclass = type(superclass_name, bases, {'_register': False})

        @AddMethod(superclass)
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

        @AddMethod(superclass)
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

        return (superclass,)

    @classmethod
    def _setup_bound_dimension(
        cls, dimension, columns, orm_name, name, bases, nmspc
    ):
        """Bind a dimension to the model, creating a code for each record."""

        if dimension is True:
            dimension = {}
        elif isinstance(dimension, basestring):
            dimension = {'name': dimension}

        dimension_name = dimension.get('name', None)
        if dimension_name is None:
            dimension_name = nmspc.get('_description', False) or orm_name

        column = dimension.get('column', 'analytic_id')

        ref_module = dimension.get('ref_module', 'analytic_structure')

        ref_id = dimension.get('ref_id', None)
        if ref_id is None:
            ref_id = orm_name.replace('.', '_') + "_analytic_dimension_id"

        # To use an inherited, renamed parent field, you have to give its name.
        sync_parent = dimension.get('sync_parent', False)
        if sync_parent is True:
            sync_parent = nmspc.get('_parent_name', 'parent_id')

        # By default, only use inherits if we can be sure there are no 'name'
        # or 'code_parent_id' field.
        use_inherits = dimension.get('use_inherits', None)
        if use_inherits is None:
            use_inherits = not (
                any(col in columns for col in ('name', 'code_parent_id'))
                or nmspc.get('_inherits', False)
                or nmspc.get('_inherit', False)
            )

        if use_inherits:
            inherits = nmspc.get('_inherits', {})
            inherits['analytic.code'] = column
            nmspc['_inherits'] = inherits

        # Default column for the underlying analytic code.
        if column not in columns:
            columns[column] = fields.many2one(
                'analytic.code',
                u"Bound Analytic Code",
                required=True,
                ondelete='restrict'
            )

        # In order to preserve inheritance, possible overrides, and OEMetaSL's
        # expected behavior, work on a new class that inherits the given bases,
        # then make our model class inherit from this class.
        superclass_name = '_{name}_SuperDimension'.format(name=name)
        # Set _register to False in order to prevent its instantiation.
        superclass = type(superclass_name, bases, {'_register': False})

        @AddMethod(superclass)
        def __init__(self, pool, cr):
            """Load or create the analytic dimension bound to the model."""

            super(superclass, self).__init__(pool, cr)

            data_osv = self.pool.get('ir.model.data')
            try:
                self._bound_dimension_id = data_osv.get_object_reference(
                    cr, SUPERUSER_ID, ref_module, ref_id
                )[1]
            except ValueError:
                vals = {'name': dimension_name, 'validated': True}
                self._bound_dimension_id = data_osv._update(
                    cr, SUPERUSER_ID, 'analytic.dimension', ref_module, vals,
                    xml_id=ref_id, noupdate=True
                )

        @AddMethod(superclass)
        def create(self, cr, uid, vals, context=None):
            """Create the analytic code."""

            code_vals = {
                'name': vals.get('name'),
                'nd_id': self._bound_dimension_id,
                'active': True,
            }
            if sync_parent:
                cp = self._get_code_parent(cr, uid, vals, context=context)
                if cp is not None:
                    code_vals['code_parent_id'] = cp

            if use_inherits:
                vals.update(code_vals)
            else:
                code_osv = self.pool.get('analytic.code')
                code_id = code_osv.create(cr, uid, code_vals, context=context)
                vals[column] = code_id

            return super(superclass, self).create(
                cr, uid, vals, context=context
            )

        if sync_parent:
            # This function is called as a method and can be overridden.
            @AddMethod(superclass)
            def _get_code_parent(self, cr, uid, vals, context=None):
                """If parent_id is in the submitted values, return the analytic
                code of this parent, to be used as the child's code's parent.
                """
                parent_id = vals.get(sync_parent, None)
                if parent_id is not None:
                    if parent_id:
                        return self.read(
                            cr, uid, parent_id, [column], context=context
                        )[column][0]
                    else:
                        return False
                return None

        if sync_parent or not use_inherits:
            @AddMethod(superclass)
            def write(self, cr, uid, ids, vals, context=None):
                """Update the analytic code's name if it is not inherited,
                and its parent code if parent-child relations are synchronized.
                """

                code_vals = {}

                if sync_parent:
                    cp = self._get_code_parent(cr, uid, vals, context=context)
                    if cp is not None:
                        code_vals['code_parent_id'] = cp

                if use_inherits:
                    vals.update(code_vals)
                else:
                    if 'name' in vals:
                        code_vals['name'] = vals.get('name')
                    if code_vals:
                        code_osv = self.pool.get('analytic.code')
                        records = self.browse(cr, uid, ids, context=context)
                        code_ids = [getattr(rec, column).id for rec in records]
                        code_osv.write(
                            cr, uid, code_ids, code_vals, context=context
                        )

                return super(superclass, self).write(
                    cr, uid, ids, vals, context=context
                )

        return (superclass,)
