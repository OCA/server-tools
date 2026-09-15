This module requires:

- A reachable ClickHouse server.
- Python dependency `clickhouse-driver` available in the Odoo environment.
- A ClickHouse database created in advance (the module does **not** create databases/users/grants).
- A ClickHouse user with at least:
  - `INSERT` and `CREATE TABLE` privileges on the target database.

> ClickHouse installation (Docker guide):
> `https://clickhouse.com/docs/install/docker`

Steps:

- Make sure `clickhouse-driver` is available in your system.
- Install the module.
- Configure the connection parameters in Odoo:
  - **Settings > Technical > Auditlog > Clickhouse configuration**
  - Fill in the following parameters:

| Field |
|:-----|
| Hostname or IP |
| TCP port |
| ClickHouse database name |
| ClickHouse user |
| ClickHouse Password |
| queue_job_batch_size (default = 1000) |
| channel_id (default root) |

- Click **Test connection**.
- Optionally, click **Create Auditlog Tables** to create the tables in the target database.
