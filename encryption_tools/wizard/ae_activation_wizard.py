from openerp import api,fields,_
from openerp.exceptions import Warning
from openerp.models import TransientModel

class AEActivationWizard(TransientModel):
    _name = "ae.activation.wizard"

    def _get_key(self):
        active_id = self.env.context.get("active_id")
        return self.key_pair_id.browse(active_id)

    key_pair_id = fields.Many2one("ae.key.pair",string="Key Pair",default=_get_key)
    password = fields.Char(string="New Password")
    password_verify = fields.Char(string="Verify New Password")

    @api.multi
    def do_activate(self):
        if self.password != self.password_verify:
            raise Warning("The passwords do not match!")

        self.key_pair_id.do_activate(self.password)
        self.password = ""
        self.password_verify = ""
        
        return {}

