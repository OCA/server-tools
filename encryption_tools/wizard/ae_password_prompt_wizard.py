from openerp import api,fields,_
from openerp.exceptions import Warning
from openerp.models import TransientModel
import pickle
#This is a helper wizard that will make it easy to prompt for a password that can be used to 
# access the private key of a key pair. The way to use this is to create a server action which will
# call the invoke method, and pass in a dictionary of the action. When the forward wizard is invoked, the 
# context will contain the password that was entered in the 'pw_wiz_result' key in the context

class PasswordPromptWizard(TransientModel):
    _name = "ae.password.prompt.wizard"

    name = fields.Char(string="Message",readonly=True)
    password = fields.Char(string="Password")
    next_action = fields.Char(string="Next action (Pickled dict as string)")

    @api.model
    def invoke(self,action_dict,message="Please enter the password to continue"):
        view_id = self.env.ref("asymmetric_encryption_willow.ae_password_prompt_wiz_view",False).id
        wiz = self.env["ae.password.prompt.wizard"].create({"name":message})
        ctx = self.env.context.copy()
        wiz.next_action = pickle.dumps(action_dict)
        return {
            "type":"ir.actions.act_window",
            "name":"Password Required",
            "view_mode":"form",
            "view_type":"form",
            "views":[(view_id,"form")],
            "view_id":view_id,
            "res_model":"ae.password.prompt.wizard",
            "res_id":wiz.id,
            "context":ctx,
            "target":"new",
        }

    @api.multi
    def do_next_action(self):
        next_action_dict = pickle.loads(self.next_action)
        ctx = self.env.context.copy()
        self.password = ""
        return next_action_dict