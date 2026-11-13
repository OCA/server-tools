# Copyright 2026 Heligrafics Fotogrametria S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression

PAST_BOUND_OPERATORS = (">", ">=", "=")
FUTURE_BOUND_OPERATORS = ("<", "<=", "=")


class SearchDateWindowMixin(models.AbstractModel):
    """Add a date window to every search that doesn't bound the date itself.

    Inheriting models set the field and the number of days of each side of the
    window. A side with no field or with ``None`` days is not applied.
    """

    _name = "search.date.window.mixin"
    _description = "Search Date Window Mixin"

    # Lower bound: field >= now - days
    _date_window_past_field = None
    _date_window_past_days = None
    # Upper bound: field < now + days
    _date_window_future_field = None
    _date_window_future_days = None
    # Context key that disables the window when set to a falsy value
    _date_window_context_key = "date_window_test"

    @api.model
    def _date_window_active(self):
        return self.env.context.get(self._date_window_context_key, True)

    @api.model
    def _date_window_bound_fields(self):
        """Return the fields whose explicit condition stops the window."""
        return {
            fname
            for fname in (self._date_window_past_field, self._date_window_future_field)
            if fname
        }

    @api.model
    def _date_window_is_bounded(self, domain, operators):
        """Tell whether ``domain`` already bounds the date with ``operators``.

        A condition on ``id`` also counts: the records are already known.
        Only the leaves are checked, not the boolean operators around them.
        """
        fnames = self._date_window_bound_fields()
        return any(
            isinstance(leaf, list | tuple)
            and len(leaf) == 3
            and (leaf[0] == "id" or (leaf[0] in fnames and leaf[1] in operators))
            for leaf in domain
        )

    @api.model
    def _date_window_limit(self, fname, days):
        """Return now plus ``days`` (negative for the past) in the type of ``fname``."""
        if self._fields[fname].type == "date":
            return fields.Date.add(fields.Date.context_today(self), days=days)
        return fields.Datetime.add(fields.Datetime.now(), days=days)

    @api.model
    def _date_window_domain(self, domain):
        """Return ``domain`` restricted to the date window when it needs it."""
        if not self._date_window_active():
            return domain
        extra = []
        past_field = self._date_window_past_field
        past_days = self._date_window_past_days
        if (
            past_field
            and past_days is not None
            and not self._date_window_is_bounded(domain, PAST_BOUND_OPERATORS)
        ):
            limit = self._date_window_limit(past_field, -past_days)
            extra.append([(past_field, ">=", limit)])
        future_field = self._date_window_future_field
        future_days = self._date_window_future_days
        if (
            future_field
            and future_days is not None
            and not self._date_window_is_bounded(domain, FUTURE_BOUND_OPERATORS)
        ):
            limit = self._date_window_limit(future_field, future_days)
            extra.append([(future_field, "<", limit)])
        if not extra:
            return domain
        return expression.AND([domain, *extra])

    def _without_date_window(self):
        """Return ``self`` without the window, unless the context sets it explicitly."""
        if self._date_window_context_key in self.env.context:
            return self
        return self.with_context(**{self._date_window_context_key: False})

    def _where_calc(self, domain, active_test=True):
        # _search, _read_group, Many2many.read and the many2many subqueries of
        # _field_to_sql all build their WHERE clause here
        return super()._where_calc(
            self._date_window_domain(domain), active_test=active_test
        )

    def _fetch_field(self, field):
        # Reading a relational field by attribute access returns all the
        # related records, not only the ones in the window
        return super(SearchDateWindowMixin, self._without_date_window())._fetch_field(
            field
        )

    def _modified_triggers(self, tree, create=False):
        # To invalidate stored computed fields, Odoo finds the dependent records
        # with a search when the relation has no inverse field. Old records must
        # be found too, or they keep a stale value
        return super(
            SearchDateWindowMixin, self._without_date_window()
        )._modified_triggers(tree, create)
