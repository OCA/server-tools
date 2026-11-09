> - log only operations triggered by some users (currently it logs all
>   users)
> - log `read_group` calls (grouped views, pivot and graph): grouping by
>   a field returns all its distinct values, but no record ids, so these
>   reads need logs that are not bound to a record
> - log the other reads that do not go through `read`, `search_read` or
>   `export_data`: `copy_data`, binary downloads, reports, and field
>   values read directly on records
