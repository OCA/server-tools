Admin password become a passkey for all active logins
=====================================================

Functionality :
---------------
* Administrator has now the possibility to login in with any login;
* By default, Odoo will send a mail to user and admin to indicate them;
* If a user and the admin have the same password, admin will be informed;

Technical information :
-----------------------
* Created two ir_config_parameter to enable / disable mail sending:
  * auth_admin_passkey.send_to_admin
  * auth_admin_passkey.send_to_user

Copyright, Author and Licence :
-------------------------------
* Copyright : 2014, Groupement Régional Alimentaire de Proximité;
* Author : Sylvain LE GAL (https://twitter.com/legalsylvain);
* Licence : AGPL-3 (http://www.gnu.org/licenses/)
