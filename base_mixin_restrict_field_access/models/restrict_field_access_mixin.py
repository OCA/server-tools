# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from lxml import etree

from odoo import api, fields, models
from odoo.api import SUPERUSER_ID
from odoo.exceptions import AccessError
from odoo.fields import Domain


class RestrictFieldAccessMixin(models.AbstractModel):
    """Mixin to restrict access to fields on record level"""

    _name = "restrict.field.access.mixin"
    _description = "Restrict Field Access Mixin"

    # use this field on your forms to be able to hide gui elements
    restrict_field_access = fields.Boolean(
        "Field access restricted", compute="_compute_restrict_field_access"
    )

    def _has_field_access(self, field, operation):
        """Extend field access check with record-level restrictions.

        For fields protected by ``groups``, the ORM group-level check may pass
        while the mixin's record-level check should deny access (e.g. a club
        manager accessing a player outside their club).  Without this override
        direct attribute access (``record.login``) would bypass the restriction
        because ``Field.__get__`` only calls ``_has_field_access`` / groups.
        """
        if not super()._has_field_access(field, operation):
            return False
        # Only layer record-level restrictions on fields that declare groups;
        # fields without groups are handled by the _read_format override.
        if not field.groups:
            return True
        if self._restrict_field_access_get_is_suspended():
            return True
        # Prevent recursion: when the mixin check reads other fields
        # (e.g. club_member_ids), those accesses must not trigger the
        # mixin check again.
        if self.env.context.get("__rfa_checking"):
            return True
        checking = self.with_context(__rfa_checking=True)
        return all(
            rec._restrict_field_access_is_field_accessible(field.name, operation)
            for rec in checking
        )

    def _compute_restrict_field_access(self):
        """determine if restricted field access is active on records.
        If you override _restrict_field_access_is_field_accessible to make
        fields accessible depending on some other field values, override this
        to in order to append an @api.depends that reflects this"""
        for rec in self:
            rec.restrict_field_access = any(
                not rec._restrict_field_access_is_field_accessible(field, "write")
                for field in self._fields
            )

    @api.model_create_multi
    def create(self, vals_list):
        restricted_vals_list = [
            self._restrict_field_access_filter_vals(vals, action="create")
            for vals in vals_list
        ]
        return (
            super(
                RestrictFieldAccessMixin,
                self._restrict_field_access_suspend(),
            )
            .create(restricted_vals_list)
            .with_env(self.env)
        )

    def copy(self, default=None):
        copies = self.browse()
        for rec in self:
            restricted_default = rec._restrict_field_access_filter_vals(
                default or {}, action="create"
            )
            new_rec = super(
                RestrictFieldAccessMixin,
                rec._restrict_field_access_suspend(),
            ).copy(default=restricted_default)
            copies |= new_rec
        return copies.with_env(self.env)

    def _read_format(self, fnames, load="_classic_read"):
        result = super()._read_format(fnames=fnames, load=load)
        if self._restrict_field_access_get_is_suspended():
            return result
        for vals in result:
            rec = self.browse(vals["id"])
            for fname in fnames:
                if fname not in self._fields:
                    continue
                if not rec._restrict_field_access_is_field_accessible(fname):
                    logging.warning(
                        "User %s accessed field %s of record %s[%s] which should be "
                        "restricted",
                        self.env.user.id,
                        fname,
                        self._name,
                        vals["id"],
                    )
                    raise AccessError(self.env._("Access to unauthorized field"))
        return result

    def _export_rows(self, fields, *, _is_toplevel_call=True):
        """Null inaccessible fields"""
        result = []
        for rec in self:
            rows = super(
                RestrictFieldAccessMixin,
                rec._restrict_field_access_suspend(),
            )._export_rows(
                fields,
                _is_toplevel_call=_is_toplevel_call,
            )
            for row in rows:
                for i, path in enumerate(fields):
                    # we only need to take care of our own fields, super calls
                    # _export_rows again for x2x exports
                    if not path or len(path) > 1:
                        continue
                    if (
                        not rec._restrict_field_access_is_field_accessible(
                            path[0],
                        )
                        and row[i]
                    ):
                        field = self._fields[path[0]]
                        row[i] = field.convert_to_export(False, rec)
            result.extend(rows)
        return result

    def write(self, vals):
        for rec in self:
            # this way, we get the minimal values we can write on all records
            vals = rec._restrict_field_access_filter_vals(vals, action="write")
        return super().write(vals)

    @api.model
    def _search(
        self,
        domain,
        offset=0,
        limit=None,
        order=None,
        *,
        active_test=True,
        bypass_access=False,
    ):
        if not domain:
            return super()._search(
                domain,
                offset=offset,
                limit=limit,
                order=order,
                active_test=active_test,
                bypass_access=bypass_access,
            )
        normalized_domain = Domain(domain)
        has_inaccessible_field = any(
            not self._restrict_field_access_is_field_accessible(
                term.field_expr.split(".")[0], "read"
            )
            for term in normalized_domain.iter_conditions()
        )
        if has_inaccessible_field:
            restricted_domain = (
                self._restrict_field_access_inject_restrict_field_access_domain(domain)
            )
            if restricted_domain is not None:
                domain = restricted_domain
        return super()._search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
            active_test=active_test,
            bypass_access=bypass_access,
        )

    @api.model
    def _restrict_field_access_inject_restrict_field_access_domain(self, domain):
        """inject a proposition to restrict search results to only the ones
        where the user may access all fields in the search domain. If you
        you override _restrict_field_access_is_field_accessible to make
        fields accessible depending on some other field values, override this
        in order not to leak information.

        Implementations may mutate list domains in place for backward
        compatibility, or return a new domain object/list."""
        pass

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type != "form" or "restrict_field_access" not in self._fields:
            return arch, view

        # inject readonly attribute to make forbidden fields readonly
        for field in arch.xpath("//field"):
            self._restrict_field_access_adjust_field_attrs(field)

        self._restrict_field_access_inject_restrict_field_access_arch(arch)

        return arch, view

    @api.model
    def _restrict_field_access_inject_restrict_field_access_arch(self, arch):
        """inject the field restrict_field_access into arch if not there"""
        if arch.xpath("./field[@name='restrict_field_access']"):
            return
        etree.SubElement(
            arch,
            "field",
            {
                "name": "restrict_field_access",
                "invisible": "1",
            },
        )

    @api.model
    def _restrict_field_access_adjust_field_attrs(self, field_node):
        """inject a readonly attribute to make non-writable fields in a form
        readonly"""
        if field_node.xpath("ancestor::list"):
            return
        field_name = field_node.attrib.get("name")
        if not field_name or field_name not in self._fields:
            return
        if not self._restrict_field_access_is_field_accessible(
            field_name, action="write"
        ):
            existing_readonly = field_node.attrib.get("readonly", "")
            if existing_readonly == "1" or existing_readonly == "True":
                # already readonly
                return
            if existing_readonly:
                field_node.set(
                    "readonly",
                    f"restrict_field_access or ({existing_readonly})",
                )
            else:
                field_node.set("readonly", "restrict_field_access")

            # Remove required if the field is restricted
            existing_required = field_node.attrib.get("required", "")
            if existing_required and existing_required not in ("0", "False"):
                field_node.set(
                    "required",
                    f"not restrict_field_access and ({existing_required})",
                )

    def _restrict_field_access_get_field_whitelist(self, action="read"):
        """return whitelisted fields. Those are readable and writable for
        everyone, for the rest, it depends on your implementation of
        _restrict_field_access_is_field_accessible"""
        return models.MAGIC_COLUMNS + [
            self._rec_name,
            "display_name",
            "restrict_field_access",
        ]

    @api.model
    def _restrict_field_access_suspend(self):
        """set a marker that we don't want to restrict field access"""
        return self.sudo()

    @api.model
    def _restrict_field_access_get_is_suspended(self):
        """return True if we shouldn't check for field access restrictions"""
        return self.env.su

    def _restrict_field_access_filter_vals(self, vals, action="read"):
        """remove inaccessible fields from vals"""
        assert len(self) <= 1, (
            "This function needs an empty recordset or exactly one record"
        )
        default_vals = (
            self._restrict_field_access_suspend().copy_data()[0] if self else {}
        )
        default_vals.update(vals)
        rec = self.new(default_vals)
        return {
            key: value
            for key, value in vals.items()
            if rec._restrict_field_access_is_field_accessible(key, action=action)
        }

    def _restrict_field_access_is_field_accessible(self, field_name, action="read"):
        """return True if the current user can perform specified action on
        all records in self. Override for your own logic.
        This function is also called with an empty recordset to get a list
        of fields which are accessible unconditionally.
        Note that this function is called *very* often. Even small things
        like saying self.env.user.id instead of self.env.uid will give you a
        massive performance penalty"""
        if field_name not in self._fields:
            return True
        if (
            self._restrict_field_access_get_is_suspended()
            or self.env.uid == SUPERUSER_ID
            or not self
            and action == "read"
            and self._fields[field_name].required
        ):
            return True
        whitelist = self._restrict_field_access_get_field_whitelist(action=action)
        return field_name in whitelist
