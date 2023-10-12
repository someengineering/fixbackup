from datetime import datetime
from pathlib import Path
from argparse import Namespace
from typing import List
from .redis import backup as redis_backup, add_args as redis_add_args
from .mysql import backup as mysql_backup, add_args as mysql_add_args
from .arangodb import backup as arangodb_backup, add_args as arangodb_add_args
from ..utils import valid_hostname, valid_ip

add_args = [redis_add_args, mysql_add_args, arangodb_add_args]


def backup(args: Namespace, backup_directory: Path) -> List[Path]:
    result: List[Path] = []
    date_prefix = datetime.utcnow().strftime("%Y%m%d%H%M")

    if args.redis_host and (valid_hostname(args.redis_host) or valid_ip(args.redis_host)):
        redis_backup_file = backup_directory / f"{date_prefix}-redis-{args.redis_host}.rdb.gz"
        if redis_backup(args, redis_backup_file):
            result.append(redis_backup_file)

    if args.mysql_host and (valid_hostname(args.mysql_host) or valid_ip(args.mysql_host)):
        mysql_backup_file = backup_directory / f"{date_prefix}-mysql-{args.mysql_host}.sql.gz"
        if mysql_backup(args, mysql_backup_file):
            result.append(mysql_backup_file)

    if args.arangodb_host and (valid_hostname(args.arangodb_host) or valid_ip(args.arangodb_host)):
        arangodb_backup_file = backup_directory / f"{date_prefix}-arangodb-{args.arangodb_host}.tar.gz"
        if arangodb_backup(args, arangodb_backup_file):
            result.append(arangodb_backup_file)

    return result
