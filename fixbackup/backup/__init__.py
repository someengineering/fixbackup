from datetime import datetime
from pathlib import Path
from argparse import Namespace
from typing import List, Tuple
from .redis import backup as redis_backup, add_args as redis_add_args
from .mysql import backup as mysql_backup, add_args as mysql_add_args
from .arangodb import backup as arangodb_backup, add_args as arangodb_add_args
from ..utils import valid_hostname, valid_ip, valid_dbname

add_args = [redis_add_args, mysql_add_args, arangodb_add_args]


def backup(args: Namespace, backup_directory: Path) -> Tuple[List[Path], bool]:
    result: List[Path] = []
    all_success = True
    environment = args.environment
    date_prefix = datetime.utcnow().strftime("%Y%m%d%H%M")

    if args.redis_host and (valid_hostname(args.redis_host) or valid_ip(args.redis_host)):
        db = str(args.redis_database_number)
        if not valid_dbname(db):
            raise ValueError(f"Invalid database name: {db}")
        redis_backup_file = backup_directory / f"{environment}-{date_prefix}-redis-{args.redis_host}-{db}.rdb.gz"
        if redis_backup(args, redis_backup_file):
            result.append(redis_backup_file)
        else:
            all_success = False

    if args.mysql_host and (valid_hostname(args.mysql_host) or valid_ip(args.mysql_host)):
        if args.mysql_database:
            db = str(args.mysql_database)
            if not valid_dbname(db):
                raise ValueError(f"Invalid database name: {db}")
        else:
            db = "all"
        mysql_backup_file = backup_directory / f"{environment}-{date_prefix}-mysql-{args.mysql_host}-{db}.sql.gz"
        if mysql_backup(args, mysql_backup_file):
            result.append(mysql_backup_file)
        else:
            all_success = False

    if args.arangodb_host and (valid_hostname(args.arangodb_host)):
        if args.arangodb_database:
            db = str(args.arangodb_database)
            if not valid_dbname(db):
                raise ValueError(f"Invalid database name: {db}")
        else:
            db = "all"
        arangodb_backup_file = (
            backup_directory / f"{environment}-{date_prefix}-arangodb-{args.arangodb_host}-{db}.tar.gz"
        )
        if arangodb_backup(args, arangodb_backup_file):
            result.append(arangodb_backup_file)
        else:
            all_success = False

    return result, all_success
