This module enables connections via FTP, SFTP, FtpLs (wip).
Operations such as retrieving a file, checking if a file exists, are all centralized
in an Abstract python class, so the user can operate without even noticing what protocol
they are using. For more exquisite operations, the user may retrieve a pure connection object in a straighforward way.

TODOS:
* Implement FtpLS
* Secure everything
* Unit tests
