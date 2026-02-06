## Analyze Specific Access

1. Open **Security Visualizer** from **Settings > Technical > Security > Security Dashboard**
2. Select a **User** from the dropdown
3. Select a **Model** (e.g., `sale.order`)
4. Choose an **Operation** (read, write, create, delete)
5. Optionally enter a **Record ID** for specific record testing
6. Click **Analyze Access**
7. Review the detailed step-by-step explanation

## View Access Matrix

1. Open **Security Dashboard** from **Settings > Technical > Security**
2. Click the **Access Matrix** tab
3. Use the operation dropdown to filter by read/write/create/delete
4. Green checkmark = access allowed, Red X = access denied
5. Click any cell to see detailed analysis (coming in next version)

## Quick Analysis

1. Go to **Settings > Technical > Security > Quick Analyzer**
2. Fill in the form (user, model, operation, optional record ID)
3. Click **Analyze**
4. View results in HTML summary and JSON format

## Understanding the Analysis

**Step 1: Model-Level Access (ACL)**

Shows all `ir.model.access` rules that apply:
- Which groups grant permission
- Which specific CRUD operations are allowed
- Whether the user has the required group membership

**Step 2: Record Rules**

Shows `ir.rule` domain filters:
- **Global rules** (no groups): ALL must be satisfied - AND logic
- **Group rules**: ANY can grant access - OR logic
- Displays actual domain syntax for each rule

**Step 3: Simulation Result**

If a record ID is provided:
- Tests actual access on that specific record
- Safe, read-only simulation
- Clear explanation of final verdict (Allowed/Denied/Conditional)

## Multi-Company Security Analysis

**Analyze Company-Specific Access**

1. Open **Security Visualizer**
2. Use the multi-company analysis feature (via RPC methods)
3. View which companies a user can access data from
4. See company-related record rules

The analysis shows:
- User's assigned companies
- Current active company
- Models with company_id field
- Company-specific record rules
- Which companies grant access to records

**Company Access Matrix**

Generate a matrix showing:
- User x Company x Model permissions
- Which companies the user can access for each model
- Company-specific rule counts

## Role-Based Access Analysis

**Prerequisites**

This feature requires the `base_user_role` module to be installed.

**Analyze User Roles**

1. Open **Security Visualizer**
2. Select a user
3. View their assigned roles
4. See which groups each role grants
5. Distinguish between role-based and direct group assignments

The analysis shows:
- All roles assigned to the user
- Groups granted by each role
- Groups assigned directly (not through roles)
- Total effective groups

**Model Access with Roles**

When analyzing model access:
- See which roles grant access to the model
- Understand access through role hierarchy
- Identify if access is via role or direct group

**Enhanced Explanations**

Access decisions now include:
- Step 0: User Roles (if roles are assigned)
- Which specific roles grant the required permission
- Whether access is role-based or direct
