# © 2020 Acsone (http://www.acsone.eu)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class Base(models.AbstractModel):
    _inherit = "base"

    def partition(self, accessor):
        """Returns a dictionary forming a partition of self into a dictionary
        value/recordset for each value obtained from the accessor.
        The accessor itself can be either a string that can be passed to mapped,
        or an arbitrary function.
        Note that it is always at least as fast to pass a function,
        hence the current implementation.
        If we have a 'field.subfield' accessor such that subfield is not a relational
        then the result is a list (not hashable). Then the str(key) are used.
        In the general case a value could both not be hashable nor stringifiable,
        in a which case this function would crash.
        """
        partition = {}

        if isinstance(accessor, str):
            if "." not in accessor:
                func = lambda r: r[accessor]  # noqa: E731
            else:
                func = lambda r: r.mapped(accessor)  # noqa: E731
        else:
            func = accessor

        for record in self:
            key = func(record)
            if not key.__hash__:
                key = str(key)
            if key not in partition:
                partition[key] = record
            else:
                partition[key] += record

        return partition

    def batch(self, batch_size=None):
        """Yield successive batches of size batch_size, or ."""
        if not (batch_size or "_default_batch_size" in dir(self)):
            raise UserError(
                _(
                    "Either set up a '_default_batch_size' on the model"
                    " or provide a batch_size parameter."
                )
            )
        batch_size = batch_size or self._default_batch_size
        for i in range(0, len(self), batch_size):
            yield self[i : i + batch_size]

    def read_per_record(self, fields=None, load="_classic_read"):
        result = {}
        data_list = self.read(fields=fields, load=load)
        for d in data_list:
            key = d.pop("id")
            result[key] = d
        return result
