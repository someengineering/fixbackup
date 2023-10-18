import os
import subprocess
from pathlib import Path
from argparse import ArgumentParser, Namespace
from ..utils import BackupFile
from ..logger import log


def add_args(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument(
        "--redis-host",
        help="Redis host",
        dest="redis_host",
        type=str,
        default=os.getenv("REDIS_HOST"),
    )

    arg_parser.add_argument(
        "--redis-port",
        help="Redis port",
        dest="redis_port",
        type=int,
        default=os.getenv("REDIS_PORT", 6379),
    )

    arg_parser.add_argument(
        "--redis-username",
        help="Redis username",
        dest="redis_username",
        type=str,
        default=os.getenv("REDIS_USERNAME"),
    )

    arg_parser.add_argument(
        "--redis-password",
        help="Redis password (if any)",
        dest="redis_password",
        type=str,
        default=os.getenv("REDIS_PASSWORD"),
    )

    arg_parser.add_argument(
        "--redis-database-number",
        help="Redis database number",
        dest="redis_database_number",
        type=int,
        default=os.getenv("REDIS_DATABASE_NUMBER", 0),
    )

    arg_parser.add_argument(
        "--redis-cli-args",
        help="Extra arguments to pass to redis-cli",
        dest="redis_cli_args",
        action="append",
        default=[],
    )

    arg_parser.add_argument(
        "--redis-tls",
        help="Redis uses TLS",
        dest="redis_tls",
        action="store_true",
        default=False,
    )

    arg_parser.add_argument(
        "--redis-tls-insecure",
        help="Redis uses TLS without verifying the certificate",
        dest="redis_tls_insecure",
        action="store_true",
        default=False,
    )


def backup(args: Namespace, backup_file_path: Path, timeout: int = 900, compress: bool = True) -> bool:
    log.info("Starting Redis backup...")

    if not args.redis_host:
        return False

    env = os.environ.copy()
    command = [
        "redis-cli",
        "--rdb",
        "-",
        "-h",
        str(args.redis_host),
        "-p",
        str(args.redis_port),
        "-n",
        str(args.redis_database_number),
        *args.redis_cli_args,
    ]
    if args.redis_username:
        command.extend(["--user", args.redis_username])
    if args.redis_password:
        env["REDISCLI_AUTH"] = args.redis_password
    if args.redis_tls:
        command.append("--tls")
    if args.redis_tls_insecure:
        command.append("--insecure")

    log.debug(f"Running command: {' '.join(command)}")
    try:
        with BackupFile(backup_file_path, compress) as backup_fd:
            process = subprocess.Popen(command, stdout=backup_fd, stderr=subprocess.PIPE, env=env)
            _, stderr = process.communicate(timeout=timeout)

            if process.returncode == 0:
                log.info(f"Redis backup completed successfully. Saved to {backup_file_path}")
                if stderr:
                    log.debug(stderr.decode().strip())
                return True
            else:
                log.error(f"Redis backup failed with return code: {process.returncode}")
                if stderr:
                    log.error(stderr.decode().strip())
    except subprocess.TimeoutExpired:
        log.error(f"Redis backup failed with timeout after {timeout} seconds")
        process.kill()
        process.communicate()
    return False
