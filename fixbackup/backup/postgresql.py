import os
import subprocess
from pathlib import Path
from argparse import ArgumentParser, Namespace
from ..utils import BackupFile
from ..logger import log


def add_args(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument(
        "--pg-host",
        help="PostgreSQL host",
        dest="pg_host",
        type=str,
        default=os.getenv("PG_HOST"),
    )

    arg_parser.add_argument(
        "--pg-port",
        help="PostgreSQL port",
        dest="pg_port",
        type=int,
        default=os.getenv("PG_PORT", 5432),
    )

    arg_parser.add_argument(
        "--pg-user",
        help="PostgreSQL user",
        dest="pg_user",
        type=str,
        default=os.getenv("PG_USER", "postgres"),
    )

    arg_parser.add_argument(
        "--pg-password",
        help="PostgreSQL password",
        dest="pg_password",
        type=str,
        default=os.getenv("PG_PASSWORD"),
    )

    arg_parser.add_argument(
        "--pg-database",
        help="PostgreSQL database",
        dest="pg_database",
        type=str,
        default=os.getenv("PG_DATABASE"),
    )

    arg_parser.add_argument(
        "--pg-dump-args",
        help="Extra arguments to pass to pg_dump",
        dest="pg_dump_args",
        action="append",
        default=[],
    )


def backup(args: Namespace, backup_file_path: Path, timeout: int = 900, compress: bool = True) -> bool:
    log.info("Starting PostgreSQL backup...")

    if not args.pg_host:
        return False

    env = os.environ.copy()
    command = [
        "pg_dump",
        "-w",
        "--if-exists",
        "--inserts",
        "-h",
        str(args.pg_host),
        "-p",
        str(args.pg_port),
        "-U",
        str(args.pg_user),
        *args.pg_dump_args,
    ]
    if args.pg_database:
        command.append("-d")
        command.append(args.pg_database)
    else:
        command[0] = "pg_dumpall"

    if args.pg_password:
        env["PGPASSWORD"] = args.pg_password

    log.debug(f"Running command: {' '.join(command)}")

    try:
        with BackupFile(backup_file_path, compress) as backup_fd:
            process = subprocess.Popen(command, stdout=backup_fd, stderr=subprocess.PIPE, env=env)
            _, stderr = process.communicate(timeout=timeout)

            if process.returncode == 0:
                log.info(f"PostgreSQL backup completed successfully. Saved to {backup_file_path}")
                if stderr:
                    log.debug(stderr.decode().strip())
                return True
            else:
                log.error(f"PostgreSQL backup failed with return code: {process.returncode}")
                if stderr:
                    log.error(stderr.decode().strip())
    except subprocess.TimeoutExpired:
        log.error(f"PostgreSQL backup failed with timeout after {timeout} seconds")
        process.kill()
        process.communicate()

    return False
