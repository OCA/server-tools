This module acts as a bridge module between auth_brute_force and auth_oauth.
This module fixes the "Authentication Attempts" records from Oauth login, the 
records will be showing "Successful" with Oauth login. Oauth login will not be
allowed if the remote address is banned.
