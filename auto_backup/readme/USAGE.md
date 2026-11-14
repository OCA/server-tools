Keep your Odoo data safe with this module. Take automated back-ups,
remove them automatically and even write them to an external server
through an encrypted tunnel. You can even specify how long local backups
and external backups should be kept, automatically!

## Connect with an FTP Server

### Keep your data safe, through an SSH tunnel!

Want to go even further and write your backups to an external server?
You can with this module! Specify the credentials to the server, specify
a path and everything will be backed up automatically. This is done
through an SSH (encrypted) tunnel, thanks to paramiko, so your data is
safe!

## Verify the SFTP server identity

paramiko verifies the identity of the SFTP server by default, using the host
keys stored in the `~/.ssh/known_hosts` file of the Odoo user.

The **SFTP Host Keys** field accepts one or more OpenSSH public keys, one per
line. The usual way to fill it in is to copy the output of
`ssh-keyscan`:

    ssh-keyscan your.sftp.server

When the field is filled in, only those keys are accepted and the local
`~/.ssh/known_hosts` file is ignored. Several lines can be entered to
support key rotation or to accept several key algorithms at once.

Enable **Ignore Host Key** to skip the verification altogether; the form
shows a warning while it is enabled.

When neither the field nor the `known_hosts` file provides a key, the
connection is refused with an explanatory error. The *Test SFTP Connection*
button applies the same rules.

## Test connection

### Checks your credentials in one click

Want to make sure if the connection details are correct and if Odoo can
automatically write them to the remote server? Simply click on the ‘Test
SFTP Connection’ button and you will get message telling you if
everything is OK, or what is wrong!

## E-mail on backup failure

### Stay informed of problems, automatically!

Do you want to know if the database backup succeeded or failed?
Subscribe to the corresponding backup setting notification type.

## Run backups when you want

From the backups configuration list, press *More \> Execute backup(s)*
to manually execute the selected processes.

[![Try me on Runbot](https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas)](https://runbot.odoo-community.org/runbot/149/11.0)
