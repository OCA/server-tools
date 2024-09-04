This module extends the functionality of any model to support conditional images
(based on the record attributes) and to manage them either globally or by company.

The main goal behind this module is to avoid storing the same image multiple times.
For example, for every partner, there is a related image (most of the time, it's the default one).
With this module properly set up, it will be stored only one time and you can change it whenever you want for all partners.

**WARNING**: this module cannot be used on the same objects using the module `base_multi_image`.
