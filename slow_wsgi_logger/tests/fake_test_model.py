import time

from odoo import api, models


class FakeTestModel(models.Model):

    _name = "fake.test"
    _description = "Fake model to test JsonRequest"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        # here simulate time computations re-using name attribute with wait value
        try:
            time.sleep(float(name))
            return []
        except Exception:
            # silently ignore exceptions
            pass
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
