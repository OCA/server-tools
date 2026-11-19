No configuration needed. After installation, access the module via:

**Menu Location**: Settings > Technical > Security > Security Visualizer

1. **Security Dashboard** - Main interactive visualizer
2. **Quick Analyzer** - Simple wizard for quick analysis

## Access Control

By default, only users in the **Settings** group (`base.group_system`) can access this module.

This ensures that sensitive security information is only visible to system administrators.

## Multi-Company Configuration

The multi-company analysis feature works automatically if your Odoo instance uses multiple companies:

* **No additional configuration needed**
* Analysis automatically detects models with `company_id` fields
* Shows which companies each user belongs to
* Identifies company-specific record rules

## Role-Based Access (Optional)

To use the role-based access analysis feature:

1. **Install base_user_role module**:
   ```bash
   # The module is typically available from OCA
   # Add the OCA server-backend repository to your addons path
   ```

2. **Assign roles to users**:
   - Go to **Settings > Users & Companies > Roles**
   - Create roles with appropriate groups
   - Assign roles to users

3. **Use the analyzer**:
   - The Security Visualizer will automatically detect installed roles
   - Analysis will include role information
   - See which roles grant access to models

If `base_user_role` is not installed:
- The module works normally without role features
- Role-related methods return appropriate status messages
- All other features remain fully functional
