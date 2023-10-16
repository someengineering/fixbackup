import os
import subprocess
from pathlib import Path
from argparse import ArgumentParser, Namespace
from ..utils import BackupFile
from ..logger import log


def add_args(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument(
        "--mysql-host",
        help="MySQL host",
        dest="mysql_host",
        type=str,
        default=os.getenv("MYSQL_HOST"),
    )

    arg_parser.add_argument(
        "--mysql-port",
        help="MySQL port",
        dest="mysql_port",
        type=int,
        default=os.getenv("MYSQL_PORT", 3306),
    )

    arg_parser.add_argument(
        "--mysql-user",
        help="MySQL user",
        dest="mysql_user",
        type=str,
        default=os.getenv("MYSQL_USER", "root"),
    )

    arg_parser.add_argument(
        "--mysql-password",
        help="MySQL password",
        dest="mysql_password",
        type=str,
        default=os.getenv("MYSQL_PASSWORD"),
    )

    arg_parser.add_argument(
        "--mysql-database",
        help="MySQL database",
        dest="mysql_database",
        type=str,
        default=os.getenv("MYSQL_DATABASE"),
    )

    arg_parser.add_argument(
        "--mysqldump-args",
        help="Extra arguments to pass to mysqldump",
        dest="mysqldump_args",
        action="append",
        default=[],
    )


def backup(args: Namespace, backup_file_path: Path, timeout: int = 900, compress: bool = True) -> bool:
    log.info("Starting MySQL backup...")

    if not args.mysql_host:
        return False

    env = os.environ.copy()
    command = [
        "mysqldump",
        "--add-drop-database",
        "--add-drop-table",
        "--add-drop-trigger",
        "--single-transaction",
        "--compression-algorithms",
        "zlib",
        "--host",
        str(args.mysql_host),
        "--port",
        str(args.mysql_port),
        "--user",
        str(args.mysql_user),
        *args.mysqldump_args,
    ]
    if args.mysql_database:
        command.append(args.mysql_database)
    else:
        command.append("--all-databases")

    if args.mysql_password:
        env["MYSQL_PWD"] = args.mysql_password

    log.debug(f"Running command: {' '.join(command)}")

    try:
        with BackupFile(backup_file_path, compress) as backup_fd:
            process = subprocess.Popen(command, stdout=backup_fd, stderr=subprocess.PIPE, env=env)
            _, stderr = process.communicate(timeout=timeout)

            if process.returncode == 0:
                log.info(f"MySQL backup completed successfully. Saved to {backup_file_path}")
                if stderr:
                    log.debug(stderr.decode().strip())
                return True
            else:
                log.error(f"MySQL backup failed with return code: {process.returncode}")
                if stderr:
                    log.error(stderr.decode().strip())
    except subprocess.TimeoutExpired:
        log.error(f"MySQL backup failed with timeout after {timeout} seconds")
        process.kill()
        process.communicate()

    return False
