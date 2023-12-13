import os
from argparse import ArgumentParser, Namespace
from typing import Callable, List


def parse_args(add_args: List[Callable[[ArgumentParser], None]]) -> Namespace:
    arg_parser = ArgumentParser(prog="fixbackup", description="FIX Database Backup System")
    arg_parser.add_argument(
        "--backup-directory",
        help="Directory where backups are created",
        dest="backup_directory",
        type=str,
        default=os.getenv("BACKUP_DIRECTORY", "."),
    )
    arg_parser.add_argument(
        "-n",
        "--name",
        dest="environment",
        help="Name of the environment",
        default=os.getenv("FIX_ENVIRONMENT", "dev"),
    )

    for add_arg in add_args:
        add_arg(arg_parser)

    args = arg_parser.parse_args()

    return args
