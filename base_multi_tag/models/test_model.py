from openerp.tools import config

# This model is required only for tests.
if config.get('test_enable', False):
    from openerp.osv import orm, fields

    class TestModel(orm.Model):
        _name = 'res.tag.test.model'
        _inherit = [
            'res.tag.mixin'
        ]

        _columns = {
            'name': fields.char('Name'),
            'test_field': fields.char('test_field'),
        }












