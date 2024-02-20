This module makes importing data from CSV and Excel files optional for each user,
allowing it only for those users belonging to a specific group.
Any other user not belonging to such group will not have the "Import" button
available anywhere. The action will even be blocked internally (to prevent
XMLRPC access, for example).
