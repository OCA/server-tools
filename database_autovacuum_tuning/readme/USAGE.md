1. Install the module on the database you want to tune.
2. Go to Settings > Technical > Database Structure > Database Autovacuum
	Tuning and review the recommended thresholds and scale factors.
3. If needed, override the defaults using the following system parameters:
	- `database_autovacuum_tuning.autovacuum_vacuum_max_threshold`
	- `database_autovacuum_tuning.autovacuum_vacuum_analyze_max_threshold`
4. The configuration parameters are applied to tables by the daily cron job.
	When the number of dead tuples in a table exceeds the vacuum threshold, it
	applies the following configuration:

	```sql
	ALTER TABLE {schemaname}.{tablename} SET (
		 autovacuum_vacuum_scale_factor = 0,
		 autovacuum_vacuum_threshold = %s,
		 autovacuum_analyze_scale_factor = 0,
		 autovacuum_analyze_threshold = %s
	)
	```
5. Monitor vacuum activity and table bloat, then adjust the settings if your
	workload changes.
