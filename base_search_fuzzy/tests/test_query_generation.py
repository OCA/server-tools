# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.osv import expression
from odoo.tests.common import TransactionCase, at_install, post_install


@at_install(False)
@post_install(True)
class QueryGenerationCase(TransactionCase):

    def setUp(self):
        super(QueryGenerationCase, self).setUp()
        self.ResPartner = self.env['res.partner']
        self.TrgmIndex = self.env['trgm.index']
        self.ResPartnerCategory = self.env['res.partner.category']

    def test_fuzzy_where_generation(self):
        """Check the generation of the where clause."""
        # the added fuzzy search operator should be available in the allowed
        # operators
        self.assertIn('%', expression.TERM_OPERATORS)

        # create new query with fuzzy search operator
        query = self.ResPartner._where_calc(
            [('name', '%', 'test')], active_test=False)
        from_clause, where_clause, where_clause_params = query.get_sql()

        # the % parameter has to be escaped (%%) for the string replation
        self.assertEqual(where_clause, """("res_partner"."name" %% %s)""")

        # test the right sql query statement creation
        # now there should be only one '%'
        complete_where = self.env.cr.mogrify(
            "SELECT FROM %s WHERE %s" % (from_clause, where_clause),
            where_clause_params)
        self.assertEqual(
            complete_where,
            b'SELECT FROM "res_partner" WHERE '
            b'("res_partner"."name" % \'test\')')

    def test_fuzzy_where_generation_translatable(self):
        """Check the generation of the where clause for translatable fields."""
        ctx = {'lang': 'de_DE'}

        # create new query with fuzzy search operator
        query = self.ResPartnerCategory.with_context(ctx)\
            ._where_calc([('name', '%', 'Goschaeftlic')], active_test=False)
        from_clause, where_clause, where_clause_params = query.get_sql()

        # the % parameter has to be escaped (%%) for the string replation
        self.assertIn("""SELECT id FROM temp_irt_current WHERE name %% %s""",
                      where_clause)

        complete_where = self.env.cr.mogrify(
            "SELECT FROM %s WHERE %s" % (from_clause, where_clause),
            where_clause_params)

        self.assertIn(
            b"""SELECT id FROM temp_irt_current WHERE name % 'Goschaeftlic'""",
            complete_where)

    def test_fuzzy_order_generation(self):
        """Check the generation of the where clause."""
        order = "similarity(%s.name, 'test') DESC" % self.ResPartner._table
        query = self.ResPartner._where_calc(
            [('name', '%', 'test')], active_test=False)
        order_by = self.ResPartner._generate_order_by(order, query)
        self.assertEqual(' ORDER BY %s' % order, order_by)

    def test_fuzzy_search(self):
        """Test the fuzzy search itself."""
        if self.TrgmIndex._trgm_extension_exists() != 'installed':
            return

        if not self.TrgmIndex.index_exists('res.partner', 'name'):
            field_partner_name = self.env.ref('base.field_res_partner_name')
            self.TrgmIndex.create({
                'field_id': field_partner_name.id,
                'index_type': 'gin',
            })

        partner1 = self.ResPartner.create({
            'name': 'John Smith'
        })
        partner2 = self.ResPartner.create(
            {'name': 'John Smizz'}
        )
        partner3 = self.ResPartner.create({
            'name': 'Linus Torvalds'
        })

        res = self.ResPartner.search([('name', '%', 'Jon Smith')])
        self.assertIn(partner1.id, res.ids)
        self.assertIn(partner2.id, res.ids)
        self.assertNotIn(partner3.id, res.ids)

        res = self.ResPartner.search([('name', '%', 'Smith John')])
        self.assertIn(partner1.id, res.ids)
        self.assertIn(partner2.id, res.ids)
        self.assertNotIn(partner3.id, res.ids)
