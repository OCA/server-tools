# Mail Server Manager

[![Odoo Version](https://img.shields.io/badge/Odoo-19.0-purple.svg)](https://www.odoo.com)
[![License](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

Professional email account management for Odoo 19 with docker-mailserver integration.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Security](#security)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Email Account Management**: Create, update, delete email accounts directly from Odoo
- **Docker-mailserver Integration**: Automatic postfix-accounts.cf configuration
- **Secure Password Management**: PBKDF2-SHA512 hashing, secure random generation
- **User Integration**: Link email accounts to Odoo users with automatic SMTP/IMAP setup
- **Password Change Wizard**: Secure two-step verification for mail password changes
- **Activity Tracking**: Full chatter integration with field tracking
- **Multi-language**: French translation included
- **Enterprise Security**: Atomic file operations, backup creation, rate limiting

## Requirements

- Odoo 19.0
- docker-mailserver (with shared volume for config files)
- Python packages: `passlib` (included in Odoo)

## Installation

### Via Docker

```bash
# Mount the module in your docker-compose.yml
volumes:
  - ./addons/mail_server_manager:/mnt/extra-addons/mail_server_manager
```

### Manual Installation

```bash
# Copy to addons folder
cp -r mail_server_manager /path/to/odoo/addons/

# Update module list and install
odoo-bin -d your_database -u mail_server_manager
```

## Configuration

Navigate to **Settings → General Settings → Mail Server Manager**:

| Setting         | Description                            | Default               |
| --------------- | -------------------------------------- | --------------------- |
| Mail Domain     | Your email domain (e.g., company.com)  | -                     |
| Config Path     | Path to docker-mailserver config files | /etc/odoo/mail_config |
| SMTP Host       | Outgoing mail server hostname          | mail                  |
| IMAP Host       | Incoming mail server hostname          | mail                  |
| IMAP Port       | IMAP SSL port                          | 993                   |
| Auto-create     | Create mailbox when creating Odoo user | False                 |
| Overwrite Email | Replace user's email with mail account | False                 |

## Usage

### For Administrators

1. Go to **Settings → Mail Server → Email Accounts**
2. Click **Create** to add a new email account
3. Fill in the email address and optionally link to an Odoo user
4. Click **Activate** to create the mailbox on the server

### For Users

1. Go to **Preferences** (user menu → My Profile)
2. Find the **Mail Server** tab
3. Click **Change Password** to update your mail password
4. Enter your Odoo password for verification, then set new mail password

## API Reference

### Models

#### `mail.server.account`

Main model for email accounts.

| Field                 | Type      | Description                      |
| --------------------- | --------- | -------------------------------- |
| `email`               | Char      | Email address (unique, required) |
| `user_id`             | Many2one  | Linked Odoo user                 |
| `state`               | Selection | draft, active, suspended, error  |
| `quota_mb`            | Integer   | Mailbox quota in MB              |
| `last_password_reset` | Datetime  | Last password reset timestamp    |

**Methods:**

- `action_reset_password()` - Generate and set new random password
- `action_suspend()` - Suspend the email account
- `action_activate()` - Activate/reactivate the account
- `action_recover_from_error()` - Recover from error state
- `action_sync_from_server()` - Import accounts from postfix-accounts.cf

#### `mail.server.manager.mixin`

AbstractModel providing configuration access.

| Method                    | Returns | Description              |
| ------------------------- | ------- | ------------------------ |
| `_get_mail_domain()`      | str     | Configured mail domain   |
| `_get_mail_config_path()` | str     | Validated config path    |
| `_get_smtp_host()`        | str     | SMTP server hostname     |
| `_get_imap_host()`        | str     | IMAP server hostname     |
| `_get_imap_port()`        | int     | IMAP port (default: 993) |

### System Parameters

| Parameter                         | Description           |
| --------------------------------- | --------------------- |
| `mail_server_manager.mail_domain` | Email domain          |
| `mail_server_manager.config_path` | Docker config path    |
| `mail_server_manager.smtp_host`   | SMTP hostname         |
| `mail_server_manager.imap_host`   | IMAP hostname         |
| `mail_server_manager.imap_port`   | IMAP port             |
| `mail_server_manager.auto_create` | Auto-create mailboxes |

## Security

- **Password Hashing**: PBKDF2-SHA512 with 600,000 iterations
- **Email Validation**: Strict regex pattern validation
- **Path Traversal Prevention**: Config path validation
- **Rate Limiting**: Maximum 3 password resets per hour per account
- **Record Rules**: Users can only view their own mail account
- **Two-Step Verification**: Odoo password required before mail password change

## Testing

```bash
# Run all module tests
odoo-bin -d testdb -i mail_server_manager --test-enable --stop-after-init

# Run specific test class
odoo-bin -d testdb --test-tags mail_server_manager
```

## Troubleshooting

### Common Issues

**Password verification fails:**

- Ensure the user has a valid Odoo password set
- Check that PBKDF2-SHA512 hash format is correct in database

**Mail account not syncing:**

- Verify the config_path is accessible by Odoo
- Check file permissions on postfix-accounts.cf

**IMAP/SMTP connection fails:**

- Verify mail server hostname resolves correctly
- Check SSL/TLS certificates are valid

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

## License

This module is licensed under LGPL-3. See
[LICENSE](https://www.gnu.org/licenses/lgpl-3.0) for details.

## Author

**KHALID SAHIH | Sudo System** Website: [sudosystem.com](https://sudosystem.com/) Email:
khalid.sahih@sudosystem.com GitHub:
[github.com/sudosystem-git](https://github.com/sudosystem-git)
