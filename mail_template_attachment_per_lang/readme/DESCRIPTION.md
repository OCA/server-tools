This module extends the functionality of mail templates.

It allows you to configure attachments based on the language of the
partner or the language configured in the mail template (which is some
times different from the partner's language).

- The email template's language could be `{{ object.partner_id.lang }}`
  or `{{ object.user_id.lang }}`, where in the first case we want to
  send the email in the partner's language and in the second case we
  want to send the email in the user's language.

For example you can use it to localize your company's terms of
agreements.
