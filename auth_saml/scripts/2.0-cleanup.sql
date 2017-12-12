--remove the old column from res.users
ALTER TABLE res_users DROP COLUMN IF EXISTS saml_access_token;
