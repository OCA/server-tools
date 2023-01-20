# Copyright 2016 ForgeFlow S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 LasLabs Inc.
# Copyright 2020 NextERP SRL.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tools import query

Oridinal_Query_obj = query.Query


def percent_search_fuzzy(self, where_claus):
    if " % " in " ".join(where_claus):
        new_where_clause = [x.replace(" % ", " %% ") for x in where_claus]
        return tuple(new_where_clause)
    return where_claus


Oridinal_Query_obj.percent_search_fuzzy = percent_search_fuzzy


# @property
def where_clause_new(self):
    ok_where = self.percent_search_fuzzy(self._where_clausess)
    return tuple(ok_where)


# original return(self._where_clausess)
Oridinal_Query_obj.where_clause = where_clause_new


def get_sql_new(self):
    """Returns (query_from, query_where, query_params)."""
    tables = [query._from_table(table, alias) for alias, table in self._tables.items()]
    joins = []
    params = []
    for alias, (kind, table, condition, condition_params) in self._joins.items():
        joins.append(f"{kind} {query._from_table(table, alias)} ON ({condition})")
        params.extend(condition_params)

    from_clause = " ".join([", ".join(tables)] + joins)
    ok_where = self.percent_search_fuzzy(self._where_clauses)
    where_clause = " AND ".join(ok_where)
    # original where_clause = " AND ".join(self._where_clauses)
    return from_clause, where_clause, params + self._where_params


Oridinal_Query_obj.get_sql = get_sql_new
