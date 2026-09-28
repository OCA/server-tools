To manage all stored images, you need to:

- Go to *Settings \> Technical \> Multi images*.

... but you probably prefer to manage them from the forms supplied by
submodules that inherit this behavior.

## Development

To develop a module based on this one:

- See module `product_multi_image` as an example.

- You have to inherit model `base_multi_image.owner` to the model that
  needs the gallery:

      class MyOwner(models.Model):
          _name = "my.model.name"
          _inherit = ["my.model.name", "base_multi_image.owner"]

          # If you need this, you will need ``pre_init_hook_for_submodules`` and
            ``uninstall_hook_for_submodules`` as detailed below.
          old_image_field = fields.Binary(related="image_1920", store=False)

- Somewhere in the owner view, add:

      <field
          name="image_ids"
          nolabel="1"
          context="{
              'default_owner_model': 'my.model.name',
              'default_owner_id': id,
          }"
          mode="kanban"/>

- If the model you are extending already had an image field, and you
  want to trick Odoo to make those images to multi-image mode, you will
  need to make use of the provided ~.hooks.post_init_hook_for_submodules
  and ~.hooks.uninstall_hook_for_submodules, like the
  `product_multi_image` module does:

      try:
          from odoo.addons.base_multi_image.hooks import (
              uninstall_hook_for_submodules,
          )
      except ImportError:
          pass


      def uninstall_hook(cr, registry):
          """Remove multi images for models that no longer use them."""
          uninstall_hook_for_submodules(cr, registry, "product.template")
          uninstall_hook_for_submodules(cr, registry, "product.product")

[![Try me on Runbot](https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas)](https://runbot.odoo-community.org/runbot/149/10.0)
