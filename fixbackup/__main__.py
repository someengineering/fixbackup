import sys
import os
import time
from pathlib import Path
from typing import List
from .logger import add_args as logging_add_args, log
from .args import parse_args
from .utils import verify_binaries
from .backup import backup, add_args as backup_add_args
from .s3 import upload_backups, add_args as s3_add_args, set_lifecycle_policy


def main() -> None:
    args = parse_args([logging_add_args, s3_add_args, *backup_add_args])
    exit_code = 0
    log.info("Starting Fix Databases Backup System")

    if not verify_binaries():
        sys.exit(1)

    if args.sleep:
        # This option is used to keep the container running for debugging purposes.
        # It allows you to connect to it inside of e.g. a K8s environment
        # and manually test the backup process. Alternatively, you could
        # override the entrypoint of the container and sleep indefinitely.
        log.info("Sleeping forever")
        try:
            while True:
                time.sleep(300)
        finally:
            log.info("Shutdown complete")
            sys.exit(0)

    backup_directory = Path(args.backup_directory)
    rmdir_backup_directory = True
    if backup_directory.exists() and not backup_directory.is_dir():
        log.critical(f"{backup_directory} exists and is not a directory")
        sys.exit(1)

    if backup_directory.exists() and not os.access(backup_directory, os.W_OK):
        log.critical(f"{backup_directory} exists and is not writable")
        sys.exit(1)

    if backup_directory.exists() and backup_directory.is_dir():
        log.debug(f"Using existing directory {backup_directory} for temporary backup files")
        rmdir_backup_directory = False

    backup_directory.mkdir(parents=True, exist_ok=True)
    backup_files: List[Path] = []

    try:
        if args.set_lifecycle_policy:
            set_lifecycle_policy(args)

        backup_files, all_success = backup(args, backup_directory)
        exit_code = 0 if all_success else 1
        if len(backup_files) > 0:
            upload_backups(args, backup_directory, backup_files)
    finally:
        for backup_file in backup_files:
            log.debug(f"Removing temporary backup file {backup_file}")
            backup_file.unlink()
        try:
            if rmdir_backup_directory:
                log.debug(f"Removing temporary directory {backup_directory}")
                backup_directory.rmdir()
        except OSError:
            pass

    if not all_success:
        exit_code = 1

    log.info("Shutdown complete")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
