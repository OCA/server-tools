# -*- coding: utf-8 -*-
# Copyright 2016 Pierre Verkest <pverkest@anybox.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ModelTestUsingSqlMatView(models.Model):

    """This model is only used to test materialized_sql_view module.
       As an example we will calulate the number of res.users per res.groups
    """
    _name = 'test.materialized.view'
    _description = u"Model used to test the module"
    _auto = False

    _inherit = [
        'abstract.materialized.sql.view',
    ]

    name = fields.Char('Name', size=64, required=True)
    group_id = fields.Many2one('res.groups', u"Group")
    user_count = fields.Integer('Users count')

    _sql_view_definition = """
            SELECT g.id, g.name, g.id as group_id, count(*) as user_count
            FROM res_groups g
                INNER JOIN res_groups_users_rel rel ON g.id = rel.gid
                INNER JOIN res_users u ON rel.uid = u.id
            GROUP BY g.id, g.name
        """
