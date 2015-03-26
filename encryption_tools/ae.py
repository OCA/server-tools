from openerp import api,fields,_
from openerp.exceptions import Warning
from openerp.models import Model
from Crypto import Cipher,Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import  PKCS1_OAEP
from Crypto.Hash import SHA256
import base64
import pycard

class EncryptionKeyPair(Model):
    _name = "ae.key.pair"

    name = fields.Char("Name")
    public_key = fields.Text("Public Key",readonly=True)
    private_key = fields.Text("Private Key",readonly=True)
    create_date = fields.Datetime("Create Date",readonly=True)
    create_uid = fields.Many2one("res.users",string="Created By",readonly=True)
    state = fields.Selection([("draft","Draft"),("active","Active")],string="State",default="draft",readonly=True)

#################################
    #testing fields and methods. Not for production. 
    
    #plain = fields.Text(string="Plaintext")
    #cipher = fields.Text(string="Ciphertext")
    #password = fields.Char(string="Password")

    #@api.one
    #def test_encrypt(self):
    #    self.cipher = self.encrypt(self.plain)

    #@api.one
    #def test_decrypt(self):
    #    self.plain = self.decrypt(self.cipher, self.password)

#################################
     
    def pad(self,text,char=">",bs=16):
        #pads text to a size that is a multiple of bs
        return text + (char * (bs - (len(text) % bs)))
    
    def de_pad(self,text,char=">"):
        #strips the specified char from the end of the text. Strip would also grab from the beginning, so it's unsuitable.
        text = text[::-1] #reverses the string.
        for c in text:
            if c == char:
                text = text[1:] #strips the first char
            else:
                break
        return text[::-1]

    @api.one
    def do_activate(self,key,bits=2048):
        #Generate public and private key pair
        generator = Random.new().read
        key_pair = RSA.generate(bits,generator)

        self.private_key = key_pair.exportKey("PEM",passphrase=key)
        self.public_key = key_pair.publickey().exportKey("PEM")
        
        self.state = "active"

    @api.multi
    def encrypt(self,text):
        #Loads the public key from this record, and pads and encrypts the supplied text.
        self.ensure_one()
        if self.state == "draft":
            raise Warning("Please set up encryption keys to securely store this data")
        public_key = RSA.importKey(self.public_key)
        cipher = PKCS1_OAEP.new(public_key)
        res = cipher.encrypt(RSA.tobytes(text))
        
        return base64.b64encode(res)

    @api.multi
    def _get_private_key(self,key):
        try:
            private_key = RSA.importKey(self.private_key,passphrase=key)
        except Exception as e:
            #An exception here is almost certainly due to the wrong key being supplied
            raise Warning("Error during decryption, possibly do to incorrect password")
        return private_key

    @api.multi
    def decrypt(self,text,key):
        self.ensure_one()
        #Load and decrypt the private key using the specified key, and then use it to 
        # decrypt the specified text.

        private_key = self._get_private_key(key)

        try:
            ciphertext = RSA.tobytes(base64.b64decode(text))
            cipher = PKCS1_OAEP.new(private_key)
            res = cipher.decrypt(ciphertext)
        except Exception as e:
            #Probably corrupted ciphertext, or wrong key is being used to decrypt
            raise Warning("Error during decryption. The encrypted text is either corrupted, or was not encrypted with this key")

        return res

    @api.multi
    def change_password(self,old_pw,new_pw):
        self.ensure_one()

        private_key = self._get_private_key(old_pw)
        
        self.private_key = private_key.exportKey("PEM",passphrase=new_pw)

    @api.multi
    def launch_activate_wizard(self):
        view_id = self.env.ref("asymmetric_encryption_willow.ae_activation_wiz_view",False).id
        wiz = self.env["ae.activation.wizard"].create({"key_pair_id":self.id})
        return {
            "type":"ir.actions.act_window",
            "name":"Activation",
            "view_mode":"form",
            "view_type":"form",
            "views":[(view_id,"form")],
            "view_id":view_id,
            "res_model":"ae.activation.wizard",
            "res_id":wiz.id,
            "target":"new",
        }

    @api.multi
    def launch_pw_change_wizard(self):
        view_id = self.env.ref("asymmetric_encryption_willow.ae_pw_change_wiz_view",False).id
        wiz = self.env["ae.pw.change.wizard"].create({"key_pair_id":self.id})
        return {
            "type":"ir.actions.act_window",
            "name":"Change Password",
            "view_mode":"form",
            "view_type":"form",
            "views":[(view_id,"form")],
            "view_id":view_id,
            "res_model":"ae.pw.change.wizard",
            "res_id":wiz.id,
            "target":"new",
        }
        

# Credic card helper functions
    
    
    @api.model
    def cc_is_valid(self,number,month,year,cvc=None,test=False):
        if len(number) < 12:
            raise Warning("Credit Card number too short. Please check and try again.")
        card = pycard.Card(number=number,month=month,year=year,cvc=cvc)
        return card.is_valid and not (test and not card.is_test)

    @api.model
    def cc_no_is_valid(self,number,test=False):
        if len(number) < 12:
            raise Warning("Credit Card number too short. Please check and try again.")
        card = pycard.Card(number=number,month=1,year=2000,cvc=None)
        return card.is_mod10_valid and not (test and not card.is_test)

    @api.model
    def cc_is_expired(self,number,month,year,cvc=None):
        card = pycard.Card(number=number,month=month,year=year,cvc=cvc)
        return card.is_expired

    @api.model
    def cc_is_expired_on_date(self,month,year,check_date):
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return True

        return (year < check_date.year) or ((year == check_date.year) and (month < check_date.month))

    #returns one of visa, mastercard, amex or unknown
    @api.model
    def get_cc_brand(self,number):
        card = pycard.Card(number=number,month=1,year=1,cvc=None)
        return card.brand

    @api.model
    def obscure_text(self,text,num_visible=4,obscure_char="*"):
        obscure_qty = len(text) - num_visible
        obscured_text = (obscure_char * obscure_qty) + text[obscure_qty:] #makes the first n digits into the obscure char,leaving the final 16 - n)
        return obscured_text

    #Intended to be called from the write method of something else. Does validation and returns a 
    # tuple of the truncated/obscured number and the encrypted number if all is valid, or 
    # raises an exception if not.
    @api.multi
    def validate_and_encrypt_cc(self,number,month,year,cvc=None,brand=None,test=False,obscure_char="*"):
        self.ensure_one()
        number = number and number.strip().replace(" ","").replace("-","") or ""
        obscure_qty = len(number) - 4
        if year and len(str(year)) != 4:
            raise Warning("Please enter a 4 digit year")
        if len(number) < 12:
            raise Warning("Credit Card number too short. Please check and try again.")
        card = pycard.Card(number,month,year,cvc)
        if card.is_expired:
            raise Warning("This card has expired.")
        elif not card.is_valid:
            raise Warning("Invalid Credit Card number supplied. Please check and try again.")
        elif (card.is_test and not test):
            raise Warning("This card is invalid. Please try a different card.")
        elif brand and (card.brand != brand) or False:
            raise Warning("The card type does not appear to be correct. Please check and try again.")
        #the card looks ok. Encrypt and obscure.
        secure_cc = self.encrypt(number)
        obscured_cc = self.obscure_text(number,num_visible=4,obscure_char=obscure_char)
        return (obscured_cc,secure_cc)



















