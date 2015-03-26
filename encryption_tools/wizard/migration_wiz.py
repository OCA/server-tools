from openerp import api,fields,_
from openerp.exceptions import Warning
from openerp.models import TransientModel
from Crypto import Cipher
from Crypto.PublicKey import RSA
from Crypto.Cipher import  AES
from Crypto import Random
from Crypto.Hash import SHA256
import base64

class AEPWChangeWizard(TransientModel):
    _name = "ae.migrate.wizard"

    def _get_key(self):
        active_id = self.env.context.get("active_id")
        return self.key_pair_id.browse(active_id)

    key_pair_id = fields.Many2one("ae.key.pair",string="Key Pair",default=_get_key)
    password = fields.Char(string="Password")
    iv = fields.Text(string="IV (Base64)")

    def de_pad(self,text,char=">"):
        #strips the specified char from the end of the text. Strip would also grab from the beginning, so it's unsuitable.
        text = text[::-1] #reverses the string.
        for c in text:
            if c == char:
                text = text[1:] #strips the first char
            else:
                break
        return text[::-1]

    @api.multi
    def do_migrate(self):
        hasher = SHA256.new()
        hasher.update(self.password)
        self.password = ""
        key = hasher.digest()
        iv = base64.b64decode(self.iv)
        cipher = AES.new(key,AES.MODE_CFB,iv)
        private_key = self.de_pad(cipher.decrypt(base64.b64decode(self.key_pair_id.private_key)))
        self.key_pair_id.private_key = private_key.exportKey("PEM",passphrase=key)

        for voucher in self.env["account.voucher.additional"].search(
                ["&",
                    ("cc_no_secure","!=",None),
                    ("cc_key_pair_id","=",self.key_pair_id.id)
            ]):
             
            ciphertext = RSA.tobytes(base64.b64decode(voucher.cc_no_secure))
            try:
                res = self.de_pad(private_key.decrypt(ciphertext),pad_char)
            except:
                #Probably corrupted ciphertext, or wrong key is being used to decrypt
                raise Warning("Error during decryption. The encrypted text is either corrupted, or was not encrypted with this key")
            voucher.cc_no_secure = self.key_pair_id.encrypt(res) 
            




