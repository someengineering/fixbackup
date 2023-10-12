import sys
import os
from pathlib import Path
from typing import List
from .logger import add_args as logging_add_args, log
from .args import parse_args
from .utils import verify_binaries
from .backup import backup, add_args as backup_add_args
from .s3 import upload_backups, add_args as s3_add_args, set_lifecycle_policy


def main() -> None:
    args = parse_args([logging_add_args, s3_add_args, *backup_add_args])
    log.info("Starting FIX Databases Backup System")

    if not verify_binaries():
        sys.exit(1)

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

        backup_files = backup(args, backup_directory)
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

    log.info("Shutdown complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
