Tool for easily translating qweb templates
==========================================

Simple Use
----------
Send mails based on a template. The template will be captured and
is visible on the Advanced tab of the mail details (only visible
in debug mode). From here the actual template can be opened and edited.

Background
----------
In some systems a large number of mail templates is in use and it is
not always easy to find where a mail comes from. Especially not if
templates (that will mostly have a noupdate xmlid) have been edited
already, or have been added through the user-interface, so can not be
found by grepping code at all.

Workflow (This has yet to be implemented)
-----------------------------------------

a. Retrieve template in specific language:
   python3 template-get.py -x <xmlid> -l <language> -p <password>

   Will retrieve template contents to stdout. Pipe to desired file.

b. Edit file:
   vim ~/tmp/hc_result.template_greetings-nl.xml

c. Put template:
   python3 template-put.py -x <xmlid> -l <language> -p <password>

   Will take template contents from stdin.
