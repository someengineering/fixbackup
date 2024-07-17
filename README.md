# `fixbackup` - Fix Database Backup System

## Usage

```bash
usage: fixbackup [-h] [--backup-directory BACKUP_DIRECTORY] [-n ENVIRONMENT] [--sleep] [--verbose | --trace | --quiet] [--s3-bucket S3_BUCKET] --type {daily,weekly,monthly,yearly} [--set-lifecycle-policy] [--redis-host REDIS_HOST]
                 [--redis-port REDIS_PORT] [--redis-username REDIS_USERNAME] [--redis-password REDIS_PASSWORD] [--redis-database-number REDIS_DATABASE_NUMBER] [--redis-cli-args REDIS_CLI_ARGS] [--redis-tls] [--redis-tls-insecure]
                 [--mysql-host MYSQL_HOST] [--mysql-port MYSQL_PORT] [--mysql-user MYSQL_USER] [--mysql-password MYSQL_PASSWORD] [--mysql-database MYSQL_DATABASE] [--mysqldump-args MYSQLDUMP_ARGS] [--pg-host PG_HOST]
                 [--pg-port PG_PORT] [--pg-user PG_USER] [--pg-password PG_PASSWORD] [--pg-database PG_DATABASE] [--pg-dump-args PG_DUMP_ARGS] [--arangodb-host ARANGODB_HOST] [--arangodb-port ARANGODB_PORT]
                 [--arangodb-username ARANGODB_USERNAME] [--arangodb-password ARANGODB_PASSWORD] [--arangodb-database ARANGODB_DATABASE] [--arangodump-args ARANGODUMP_ARGS] [--arangodb-tls]

Fix Database Backup System

options:
  -h, --help            show this help message and exit
  --backup-directory BACKUP_DIRECTORY
                        Directory where backups are created
  -n ENVIRONMENT, --name ENVIRONMENT
                        Name of the environment
  --sleep               Don't do anything, just sleep forever
  --verbose, -v         Verbose logging
  --trace               Trage logging
  --quiet               Only log errors
  --s3-bucket S3_BUCKET
                        AWS S3 bucket name
  --type {daily,weekly,monthly,yearly}
                        Type of backup to create.
  --set-lifecycle-policy
                        Set S3 bucket object lifetime policy
  --redis-host REDIS_HOST
                        Redis host
  --redis-port REDIS_PORT
                        Redis port
  --redis-username REDIS_USERNAME
                        Redis username
  --redis-password REDIS_PASSWORD
                        Redis password (if any)
  --redis-database-number REDIS_DATABASE_NUMBER
                        Redis database number
  --redis-cli-args REDIS_CLI_ARGS
                        Extra arguments to pass to redis-cli
  --redis-tls           Redis uses TLS
  --redis-tls-insecure  Redis uses TLS without verifying the certificate
  --mysql-host MYSQL_HOST
                        MySQL host
  --mysql-port MYSQL_PORT
                        MySQL port
  --mysql-user MYSQL_USER
                        MySQL user
  --mysql-password MYSQL_PASSWORD
                        MySQL password
  --mysql-database MYSQL_DATABASE
                        MySQL database
  --mysqldump-args MYSQLDUMP_ARGS
                        Extra arguments to pass to mysqldump
  --pg-host PG_HOST     PostgreSQL host
  --pg-port PG_PORT     PostgreSQL port
  --pg-user PG_USER     PostgreSQL user
  --pg-password PG_PASSWORD
                        PostgreSQL password
  --pg-database PG_DATABASE
                        PostgreSQL database
  --pg-dump-args PG_DUMP_ARGS
                        Extra arguments to pass to pg_dump
  --arangodb-host ARANGODB_HOST
                        ArangoDB host
  --arangodb-port ARANGODB_PORT
                        ArangoDB port
  --arangodb-username ARANGODB_USERNAME
                        ArangoDB username
  --arangodb-password ARANGODB_PASSWORD
                        ArangoDB password
  --arangodb-database ARANGODB_DATABASE
                        ArangoDB database to dump
  --arangodump-args ARANGODUMP_ARGS
                        Extra arguments to pass to arangodump
  --arangodb-tls        ArangoDB uses TLS
```
