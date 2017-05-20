from openerp import api,fields,_
from openerp.exceptions import Warning
from openerp.models import TransientModel

class AEPWChangeWizard(TransientModel):
    _name = "ae.pw.change.wizard"

    def _get_key(self):
        active_id = self.env.context.get("active_id")
        return self.key_pair_id.browse(active_id)

    key_pair_id = fields.Many2one("ae.key.pair",string="Key Pair",default=_get_key)
    old_password = fields.Char(string="Old Password")
    password = fields.Char(string="Password")
    password_verify = fields.Char(string="Verify Password")

    @api.multi
    def do_change_pass(self):
        if self.password != self.password_verify:
            raise Warning("The passwords do not match!")

        self.key_pair_id.change_password(self.old_password,self.password)
        self.password = ""
        self.password_verify = ""
        return {}

