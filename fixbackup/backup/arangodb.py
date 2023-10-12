import os
import subprocess
import tarfile
import tempfile
from pathlib import Path
from argparse import ArgumentParser, Namespace
from ..logger import log


def add_args(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument(
        "--arangodb-host",
        help="ArangoDB host",
        dest="arangodb_host",
        type=str,
        default=os.getenv("ARANGODB_HOST"),
    )

    arg_parser.add_argument(
        "--arangodb-port",
        help="ArangoDB port",
        dest="arangodb_port",
        type=int,
        default=os.getenv("ARANGODB_PORT", 8529),
    )

    arg_parser.add_argument(
        "--arangodb-username",
        help="ArangoDB username",
        dest="arangodb_username",
        type=str,
        default=os.getenv("ARANGODB_USERNAME", "root"),
    )

    arg_parser.add_argument(
        "--arangodb-password",
        help="ArangoDB password",
        dest="arangodb_password",
        type=str,
        default=os.getenv("ARANGODB_PASSWORD"),
    )

    arg_parser.add_argument(
        "--arangodb-database",
        help="ArangoDB database to dump",
        dest="arangodb_database",
        type=str,
        default=os.getenv("ARANGODB_DATABASE"),
    )

    arg_parser.add_argument(
        "--arangodump-args",
        help="Extra arguments to pass to arangodump",
        dest="arangodump_args",
        action="append",
        default=[],
    )


def backup(args: Namespace, backup_file_path: Path, timeout: int = 900, compress: bool = True) -> bool:
    log.info("Starting ArangoDB backup...")

    if not args.arangodb_host:
        return False

    with tempfile.TemporaryDirectory() as temp_dir:
        env = os.environ.copy()
        command = [
            "arangodump",
            "--server.endpoint",
            f"tcp://{args.arangodb_host}:{args.arangodb_port}",
            "--server.username",
            args.arangodb_username,
            "--overwrite",
            "true",
            "--output-directory",
            temp_dir,
            *args.arangodump_args,
        ]
        if args.arangodb_database:
            command.extend(["--server.database", args.arangodb_database])
        else:
            command.extend(["--all-databases", "true"])
        if args.arangodb_password:
            command.extend(["--server.password", args.arangodb_password])

        log.debug(f"Running command: {' '.join(command)}")
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            stdout, stderr = process.communicate(timeout=timeout)

            if process.returncode == 0:
                if stdout:
                    log.debug(stdout.decode().strip())
                if stderr:
                    log.debug(stderr.decode().strip())
                open_mode = "w:gz" if compress else "w"
                with tarfile.open(backup_file_path, open_mode) as tar:
                    for item in os.listdir(temp_dir):
                        tar.add(os.path.join(temp_dir, item), arcname=item)
                log.info(f"ArangoDB backup completed successfully. Saved to {backup_file_path}")
                return True
            else:
                log.error(f"ArangoDB backup failed with return code: {process.returncode}")
                if stdout:
                    log.error(stdout.decode().strip())
                if stderr:
                    log.error(stderr.decode().strip())
        except subprocess.TimeoutExpired:
            log.error(f"ArangoDB backup failed with timeout after {timeout} seconds")
            process.kill()
            process.communicate()
    return False
