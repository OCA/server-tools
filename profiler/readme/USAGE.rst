For Python profiling we have two methods:

**Full profiling**: Profile anything that happens between A and B. For this method, start Odoo
with workers=0, create a profile record and select Python method 'All activity'. Enable
the profiler, do actions in Odoo, and disable again. Under 'Attachments' you can download the
cProfile stats file.

**Profile current session per HTTP request**: Profile HTTP requests in the active user session.
This method also works in multi-worker mode. Create a profile record and select Python method
'Per HTTP request'. Enable the profiler, do actions in Odoo, and see the list filling up with
requests. After some time, disable. You can find your slow HTTP requests by sorting
on the 'Total time' column, and download the cProfile stats file for further analysis.

Stats files can be analyzed visually for example with Snakeviz or Tuna.
