import os
import boto3
from pathlib import Path
from argparse import ArgumentParser, Namespace
from typing import List, Any, Dict
from .logger import log


backup_expiration_days = {
    "daily": 7,  # 1 week
    "weekly": 28,  # 4 weeks
    "monthly": 365,  # 1 year
    "yearly": 3650,  # 10 years
}
backup_types = backup_expiration_days.keys()


def upload_backups(args: Namespace, backup_directory: Path, backup_files: List[Path]) -> None:
    if args.s3_bucket is None:
        return

    prefix = args.backup_type
    bucket_name = args.s3_bucket
    resource = boto3.resource("s3")

    log.info(f"Syncing backups to S3 bucket {bucket_name}/{prefix}")
    bucket = resource.Bucket(bucket_name)
    for backup_file in backup_files:
        print(f"Replacing {backup_file} with {backup_directory}")
        dst = str(backup_file.absolute()).replace(str(backup_directory.absolute()), "", 1).lstrip("/")
        if prefix != "":
            dst = f"{prefix}/{dst}"
        log.debug(f"Uploading {backup_file} to s3://{bucket_name}/{dst}")
        bucket.upload_file(backup_file, dst)


def set_lifecycle_policy(args: Namespace) -> None:
    if args.s3_bucket is None:
        return

    bucket_name = args.s3_bucket
    client = boto3.client("s3")

    log.info(f"Setting S3 bucket {bucket_name} object lifetime policy")
    client.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration=generate_lifecycle_policy(),
    )


def generate_lifecycle_policy() -> Dict[str, Any]:
    rules = []
    for backup_type in backup_types:
        rules.append(
            {
                "ID": f"{backup_type}_rule",
                "Prefix": f"{backup_type}/",
                "Status": "Enabled",
                "Expiration": {"Days": backup_expiration_days[backup_type]},
            }
        )
    policy = {"Rules": rules}
    return policy


def add_args(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--s3-bucket",
        dest="s3_bucket",
        help="AWS S3 bucket name",
        default=os.getenv("S3_BUCKET"),
    )
    parser.add_argument(
        "--type", choices=backup_types, dest="backup_type", required=True, help="Type of backup to create."
    )
    parser.add_argument(
        "--set-lifecycle-policy",
        dest="set_lifecycle_policy",
        action="store_true",
        help="Set S3 bucket object lifetime policy",
    )
