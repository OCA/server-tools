This module allows to prepopulate the user database with all entries in the
LDAP database.

In order to schedule the population of the user database on a regular basis,
create a new scheduled action with the following properties:

- Object: res.company.ldap
- Function: action_populate
- Arguments: [res.company.ldap.id]

Substitute res.company.ldap.id with the actual id of the res.company.ldap
object you want to query.

