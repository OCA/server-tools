Go to `Settings / Technical / Audit / Rules` to subscribe rules. A rule defines
which operations to log for a given data model.
The rule is now extended with a new field permission_ids, that tells us wich groups will
be allowed to read the lines produced by this rule.
If permission_ids is left empty, the default will be: 
"auditlog lines visible only by user in Settings group, which is the default 
for the auditlog module"


Then, check logs in the `Settings / Technical / Audit / Logs` menu. You can
group them by user sessions, date, data model , HTTP requests.
