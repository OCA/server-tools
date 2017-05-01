# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json
from lxml import etree
from openerp import _, api, fields, models, SUPERUSER_ID
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

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        """Restrict reading if we read an inaccessible field"""
        has_inaccessible_field = False
        has_inaccessible_field |= any(
            not self._restrict_field_access_is_field_accessible(f)
            for f in fields or self._fields.keys()
        )
        has_inaccessible_field |= any(
            expression.is_leaf(term) and
            not self._restrict_field_access_is_field_accessible(
                term[0].split('.')[0]
            )
            for term in domain
        )
        if groupby:
            if isinstance(groupby, basestring):
                groupby = [groupby]
            has_inaccessible_field |= any(
                not self._restrict_field_access_is_field_accessible(
                    f.split(':')[0]
                )
                for f in groupby
            )
        if orderby:
            has_inaccessible_field |= any(
                not self._restrict_field_access_is_field_accessible(f.split())
                for f in orderby.split(',')
            )
        # just like with search, we restrict read_group to the accessible
        # records, because we'd either leak data otherwise or have very wrong
        # results
        if has_inaccessible_field:
            self._restrict_field_access_inject_restrict_field_access_domain(
                domain
            )

        return super(RestrictFieldAccessMixin, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy
        )

    @api.multi
    def _BaseModel__export_rows(self, fields):
        """Null inaccessible fields"""
        result = []
        for this in self:
            rows = super(RestrictFieldAccessMixin, this)\
                ._BaseModel__export_rows(fields)
            for row in rows:
                for i, path in enumerate(fields):
                    # we only need to take care of our own fields, super calls
                    # __export_rows again for x2x exports
                    if not path or len(path) > 1:
                        continue
                    if not this._restrict_field_access_is_field_accessible(
                            path[0],
                    ) and row[i]:
                        row[i] = self._fields[path[0]].convert_to_export(
                            self._fields[path[0]].null(self.env), self.env
                        )
            result.extend(rows)
        return result

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
        # pylint: disable=R8110
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
        all records in self. Override for your own logic.
        This function is also called with an empty recordset to get a list
        of fields which are accessible unconditionally"""
        if self._restrict_field_access_get_is_suspended() or\
                self.env.user.id == SUPERUSER_ID or\
                not self and action == 'read':
            return True
        whitelist = self._restrict_field_access_get_field_whitelist(
            action=action)
        return field_name in whitelist
