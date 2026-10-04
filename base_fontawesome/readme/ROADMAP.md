- Emails draw their icons with Odoo's own Font Awesome 4.7 font, as images: icons
  new in Font Awesome 6 come out blank there.
- The `.fa-name::before` rules are loaded in the backend only, where the website
  builder and the email editors run; HTML editors of the frontend (e.g. the
  forum) still list no Font Awesome icon.
