from odoo import api, models

from ..models.ir_model import _check_access_profiled_user


class BaseModel(models.BaseModel):

    _inherit = "base"

    @api.model
    def search_read(
        self,
        domain=None,
        fields=None,
        offset=0,
        limit=None,
        order=None,
    ):
        result = super().search_read(domain, fields, offset, limit, order)
        operation = "read"
        if not self.env.su:
            _check_access_profiled_user(self.env, operation, self._name)
        return result

    @api.model
    @api.returns(
        "self",
        upgrade=lambda self, value, args, offset=0, limit=None, order=None, count=False: value
        if count
        else self.browse(value),
        downgrade=lambda self, value, args, offset=0, limit=None, order=None, count=False: value
        if count
        else value.ids,
    )
    def search(self, args, offset=0, limit=None, order=None, count=False):
        result = super().search(args, offset, limit, order, count)
        operation = "read"
        if not self.env.su:
            _check_access_profiled_user(self.env, operation, self._name)
        return result

    def read(self, fields=None, load="_classic_read"):
        result = super().read(fields, load)
        operation = "read"
        if not self.env.su:
            _check_access_profiled_user(self.env, operation, self._name)
        return result

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        result = super().read_group(
            domain, fields, groupby, offset, limit, orderby, lazy
        )
        operation = "read"
        if not self.env.su:
            _check_access_profiled_user(self.env, operation, self._name)
        return result

    def write(self, vals):
        result = super().write(vals)
        operation = "write"
        if not self.env.su:
            _check_access_profiled_user(self.env, operation, self._name)
        return result

    @api.model_create_multi
    @api.returns("self", lambda value: value.id)
    def create(self, vals):
        result = super().create(vals)
        operation = "create"
        if not self.env.su:
            _check_access_profiled_user(self.env, operation, self._name)
        return result

    def unlink(self):
        result = super().unlink()
        operation = "unlink"
        if not self.env.su:
            _check_access_profiled_user(self.env, operation, self._name)
        return result
