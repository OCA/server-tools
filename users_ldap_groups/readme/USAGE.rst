Define mappings in Settings / General Settings / LDAP Parameters

Decide whether you want only groups mapped from ldap (`Only ldap groups` checked) or a mix of manually set groups and ldap groups (`Only ldap groups` unchecked). Setting this to 'no' will result in users never losing privileges when you remove them from a ldap group, so that's a potential security issue. It is still the default to prevent losing group information by accident.

For active directory, use LDAP attribute 'memberOf' and operator 'contains'. Fill in the DN of the windows group as value and choose an Odoo group users with this windows group are to be assigned to.

For posix accounts, use operator 'query' and a value like::

    (&(cn=bzr)(objectClass=posixGroup)(memberUid=$uid))
