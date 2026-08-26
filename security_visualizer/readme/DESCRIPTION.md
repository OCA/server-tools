This module provides a comprehensive security visualization and debugging tool for Odoo.
It makes Odoo's complex security system (`ir.model.access` and `ir.rule`) understandable
and debuggable.

**Problem**

Odoo's security system is powerful but notoriously difficult to understand and debug:

* Access rules are invisible and complex
* Debugging security is painful
* Small mistakes cause major data leaks or access blocks
* No clear way to answer "Why can't user X access record Y?"

**Solution**

This module provides:

1. **Security Analyzer** - Detailed analysis of access decisions
2. **Access Matrix** - Visual grid showing user × model × operation permissions
3. **Rule Explainer** - Step-by-step breakdown of security checks
4. **Safe Simulation** - Test access as any user without risk
5. **Multi-Company Analysis** - Understand company-specific security rules
6. **Role-Based Access** - Analyze access through user roles (requires base_user_role module)
