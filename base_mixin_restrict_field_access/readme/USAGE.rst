To use this module, you need to inherit this mixin for the model whose fields
you want to restrict, and implement at least the following methods to do
something useful:

.. code:: python

    class ResPartner(models.Model):
        # inherit from the mixin
        _inherit = ['restrict.field.access.mixin', 'res.partner']
        _name = 'res.partner'

        @api.multi
        def _restrict_field_access_get_field_whitelist(self, action='read'):
            # return a whitelist (or a blacklist) of fields, depending on the
            # action passed
            whitelist = [
                'name', 'parent_id', 'is_company', 'firstname', 'lastname',
                'infix', 'initials',
            ] + super(ResPartner, self)\
                ._restrict_field_access_get_field_whitelist(action=action)
            if action == 'read':
                whitelist.extend(['section_id', 'user_id'])
            return whitelist

        @api.multi
        def _restrict_field_access_is_field_accessible(self, field_name,
                                                       action='read'):
            # in case the whitelist is not enough, you can also decide for
            # specific records if an action can be carried out on it or not
            result = super(ResPartner, self)\
                ._restrict_field_access_is_field_accessible(
                    field_name, action=action)
            if result or not self:
                return result
            return all(this.section_id in self.env.user.section_ids or
                       this.user_id == self.env.user
                       for this in self)

        @api.multi
        @api.onchange('section_id', 'user_id')
        @api.depends('section_id', 'user_id')
        def _compute_restrict_field_access(self):
            # if your decision depends on other fields, you probably need to
            # override this function in order to attach the correct onchange/
            # depends decorators
            return super(ResPartner, self)._compute_restrict_field_access()

        @api.model
        def _restrict_field_access_inject_restrict_field_access_domain(
                self, domain):
            # you also might want to decide with a domain expression which
            # records are visible in the first place
            domain[:] = expression.AND([
                domain,
                [
                    '|',
                    ('section_id', 'in', self.env.user.section_ids.ids),
                    ('user_id', '=', self.env.user.id),
                ],
            ])

The example code here will allow only reading a few fields for partners of
which the current user is neither the sales person nor in this partner's sales
team.

Read the comments of the mixin, that's part of the documentation. Also have a
look at the tests, that's another example on how to use this code.
