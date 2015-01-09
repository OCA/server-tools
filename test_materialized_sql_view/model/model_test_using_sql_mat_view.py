# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class ModelTestUsingSqlMatView(osv.Model):

    """This model is only used to test materialized_sql_view module.
       As an example we will calulate the number of res.users per res.groups
    """
    _name = 'test.materialized.view'
    _description = u"Model used to test the module"
    _auto = False

    _inherit = [
        'abstract.materialized.sql.view',
    ]

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'group_id': fields.many2one('res.groups', u"Group"),
        'user_count': fields.integer('Users count')
    }

    # This string will be stored in the database and compared later to make
    # sure it still the same request to avoid refreshing the view if not
    # necessary at upgrade time.
    # As this string will be compared with the result of the read() it should
    # be unicode string to avoid python to warn.
    _sql_view_definition = u"""
            SELECT g.id, g.name, g.id as group_id, count(*) as user_count
            FROM res_groups g
                INNER JOIN res_groups_users_rel rel ON g.id = rel.gid
                INNER JOIN res_users u ON rel.uid = u.id
            GROUP BY g.id, g.name
        """
