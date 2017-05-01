# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json
from lxml import etree
from openerp import _, api, fields, models, SUPERUSER_ID
from openerp.addons.web.controllers.main import Export
from openerp.http import request
from openerp.osv import expression  # pylint: disable=W0402


class RestrictFieldAccessMixin(models.AbstractModel):
    """Mixin to restrict access to fields on record level"""
    _name = 'restrict.field.access.mixin'

    @api.multi
    def _compute_restrict_field_access(self):
        """determine if restricted field access is active on records.
        If you override _restrict_field_access_is_field_accessible to make
        fields accessible depending on some other field values, override this
        to in order to append an @api.depends that reflects this"""
        result = {}
        for this in self:
            this['restrict_field_access'] = any(
                not this._restrict_field_access_is_field_accessible(
                    field, 'write')
                for field in self._fields)
            if this['restrict_field_access']:
                result['warning'] = {
                    'title': _('Warning'),
                    'message': _(
                        'You will lose access to fields if you save now!'),
                }
        return result

    # use this field on your forms to be able to hide gui elements
    restrict_field_access = fields.Boolean(
        'Field access restricted', compute='_compute_restrict_field_access')

    @api.model
    @api.returns('self', lambda x: x.id)
    def create(self, vals):
        restricted_vals = self._restrict_field_access_filter_vals(
            vals, action='create')
        return self.browse(
            super(RestrictFieldAccessMixin,
                  # TODO: this allows users to slip in nonallowed
                  # fields with x2many operations, so we need to reset
                  # this somewhere, probably just at the beginning of create
                  self._restrict_field_access_suspend())
            .create(restricted_vals).ids
        )

    @api.multi
    def copy(self, default=None):
        restricted_default = self._restrict_field_access_filter_vals(
            default or {}, action='create')
        return self.browse(
            super(RestrictFieldAccessMixin,
                  self._restrict_field_access_suspend())
            .copy(default=restricted_default).ids
        )

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(RestrictFieldAccessMixin, self).read(
            fields=fields, load=load)
        for record in result:
            for field in record:
                if not self._restrict_field_access_is_field_accessible(field):
                    record[field] = self._fields[field].convert_to_read(
                        self._fields[field].null(self.env))
        return result

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        """
        Remove inaccessible fields from 'fields', 'groupby' and 'orderby'.

        If this removes all 'fields', return no records.
        If this removes all 'groupby', group by first remaining field.
        If this removes 'orderby', don't specify order.
        """
        requested_fields = fields or self._columns.keys()
        sanitised_fields = [
            f for f in requested_fields if self._restrict_field_access_is_field_accessible(
                cr, uid, [], f
            )
        ]
        if not sanitised_fields:
            return []

        sanitised_groupby = []
        groupby = [groupby] if isinstance(groupby, basestring) else groupby
        for groupby_part in groupby:
            groupby_field = groupby_part.split(':')[0]
            if self._restrict_field_access_is_field_accessible(cr, uid, [], groupby_field):
                sanitised_groupby.append(groupby_part)
        if not sanitised_groupby:
            sanitised_groupby.append(sanitised_fields[0])

        if orderby:
            sanitised_orderby = []
            for orderby_part in orderby.split(','):
                orderby_field = orderby_part.split()[0]
                if self._restrict_field_access_is_field_accessible(cr, uid, [], orderby_field):
                    sanitised_orderby.append(orderby_part)
            sanitised_orderby = sanitised_orderby and ','.join(sanitised_orderby) or False
        else:
            sanitised_orderby = False

        result = super(RestrictFieldAccessMixin, self).read_group(
            cr,
            uid,
            domain,
            sanitised_fields,
            sanitised_groupby,
            offset=offset,
            limit=limit,
            context=context,
            orderby=sanitised_orderby,
            lazy=lazy
        )
        # Add inaccessible fields back in with null values
        inaccessible_fields = [f for f in requested_fields if f not in sanitised_fields]
        for field_name in inaccessible_fields:
            field = self._columns[field_name]
            if lazy:
                result.append(
                    {
                        '__domain': [(True, '=', True)],
                        field_name: field.null(self.env),
                        field_name + '_count': 0L
                    }
                )
            else:
                result.append(
                    {
                        '__domain': [(True, '=', True)],
                        field_name: field.null(self.env),
                        '__count': 0L
                    }
                )
        return result

    @api.multi
    def _BaseModel__export_rows(self, fields):
        """Don't export inaccessible fields"""
        if isinstance(self, RestrictFieldAccessMixin):
            sanitised_fields = [f for f in fields if f and self._restrict_field_access_is_field_accessible(f[0])]
            return super(RestrictFieldAccessMixin, self)._BaseModel__export_rows(sanitised_fields)
        else:
            return super(RestrictFieldAccessMixin, self)._BaseModel__export_rows(fields)

    @api.multi
    def write(self, vals):
        for this in self:
            # this way, we get the minimal values we can write on all records
            vals = this._restrict_field_access_filter_vals(
                vals, action='write')
        return super(RestrictFieldAccessMixin, self).write(vals)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        if not args:
            return super(RestrictFieldAccessMixin, self)._search(
                args, offset=offset, limit=limit, order=order, count=count,
                access_rights_uid=access_rights_uid)
        args = expression.normalize_domain(args)
        has_inaccessible_field = False
        for term in args:
            if not expression.is_leaf(term):
                continue
            if not self._restrict_field_access_is_field_accessible(
                    term[0], 'read'):
                has_inaccessible_field = True
                break
        if has_inaccessible_field:
            check_self = self if not access_rights_uid else self.sudo(
                access_rights_uid)
            check_self\
                ._restrict_field_access_inject_restrict_field_access_domain(
                    args)
        return super(RestrictFieldAccessMixin, self)._search(
            args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)

    @api.model
    def _restrict_field_access_inject_restrict_field_access_domain(
            self, domain):
        """inject a proposition to restrict search results to only the ones
        where the user may access all fields in the search domain. If you
        you override _restrict_field_access_is_field_accessible to make
        fields accessible depending on some other field values, override this
        in order not to leak information"""
        pass

    @api.cr_uid_context
    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        # This needs to be oldstyle because res.partner in base passes context
        # as positional argument
        result = super(RestrictFieldAccessMixin, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)

        if view_type == 'search':
            return result

        # inject modifiers to make forbidden fields readonly
        arch = etree.fromstring(result['arch'])
        for field in arch.xpath('//field'):
            field.attrib['modifiers'] = json.dumps(
                self._restrict_field_access_adjust_field_modifiers(
                    cr, uid,
                    field,
                    json.loads(field.attrib.get('modifiers', '{}')),
                    context=context))

        self._restrict_field_access_inject_restrict_field_access_arch(
            cr, uid, arch, result['fields'], context=context)

        result['arch'] = etree.tostring(arch, encoding="utf-8")
        return result

    @api.model
    def _restrict_field_access_inject_restrict_field_access_arch(
            self, arch, fields):
        """inject the field restrict_field_access into arch if not there"""
        if 'restrict_field_access' not in fields:
            etree.SubElement(arch, 'field', {
                'name': 'restrict_field_access',
                'modifiers': json.dumps({
                    ('tree_' if arch.tag == 'tree' else '') + 'invisible': True
                }),
            })
            fields['restrict_field_access'] =\
                self._fields['restrict_field_access'].get_description(self.env)

    @api.model
    def _restrict_field_access_adjust_field_modifiers(self, field_node,
                                                      modifiers):
        """inject a readonly modifier to make non-writable fields in a form
        readonly"""
        # TODO: this can be fooled by embedded views
        if not self._restrict_field_access_is_field_accessible(
                field_node.attrib['name'], action='write'):
            for modifier, value in [('readonly', True), ('required', False)]:
                domain = modifiers.get(modifier, [])
                if isinstance(domain, list) and domain:
                    domain = expression.normalize_domain(domain)
                elif bool(domain) == value:
                    # readonly/nonrequired anyways
                    return modifiers
                else:
                    domain = []
                restrict_domain = [('restrict_field_access', '=', value)]
                if domain:
                    restrict_domain = expression.OR([
                        restrict_domain,
                        domain
                    ])
                modifiers[modifier] = restrict_domain
        return modifiers

    @api.multi
    def _restrict_field_access_get_field_whitelist(self, action='read'):
        """return whitelisted fields. Those are readable and writable for
        everyone, for the rest, it depends on your implementation of
        _restrict_field_access_is_field_accessible"""
        return models.MAGIC_COLUMNS + [
            self._rec_name, 'display_name', 'restrict_field_access',
        ]

    @api.model
    def _restrict_field_access_suspend(self):
        """set a marker that we don't want to restrict field access"""
        # TODO: this is insecure. in the end, we need something in the lines of
        # base_suspend_security's uid-hack
        return self.with_context(_restrict_field_access_suspend=True)

    @api.model
    def _restrict_field_access_get_is_suspended(self):
        """return True if we shouldn't check for field access restrictions"""
        return self.env.context.get('_restrict_field_access_suspend')

    @api.multi
    def _restrict_field_access_filter_vals(self, vals, action='read'):
        """remove inaccessible fields from vals"""
        assert len(self) <= 1, 'This function needs an empty recordset or '\
            'exactly one record'
        this = self.new(dict((self.copy_data()[0] if self else {}), **vals))
        return dict(
            filter(
                lambda itemtuple:
                this._restrict_field_access_is_field_accessible(
                    itemtuple[0], action=action),
                vals.iteritems()))

    @api.multi
    def _restrict_field_access_is_field_accessible(self, field_name,
                                                   action='read'):
        """return True if the current user can perform specified action on
        all records in self. Override for your own logic"""
        if self._restrict_field_access_get_is_suspended() or\
                self.env.user.id == SUPERUSER_ID:
            return True
        whitelist = self._restrict_field_access_get_field_whitelist(
            action=action)
        return field_name in whitelist


class RestrictedExport(Export):
    """Don't (even offer to) export inaccessible fields"""
    def fields_get(self, model):
        Model = request.session.model(model)
        fields = Model.fields_get(False, request.context)
        model = request.env[model]
        if isinstance(model, RestrictFieldAccessMixin):
            sanitised_fields =  {k:fields[k] for k in fields if model._restrict_field_access_is_field_accessible(k)}
            return sanitised_fields
        else:
            return fields

