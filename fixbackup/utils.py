import os
import re
import threading
import ipaddress
import gzip
import shutil
from pathlib import Path
from typing import Any, Optional, Type
from types import TracebackType
from .logger import log


def verify_binaries() -> bool:
    required_binaries = ["mysqldump", "arangodump", "redis-cli"]
    for binary in required_binaries:
        log.debug(f"Verifying binary {binary} is in PATH")
        if shutil.which(binary) is None:
            log.error(f"Required binary {binary} not found in PATH")
            return False
    return True


# https://bugs.python.org/issue24358
#
# the following naive implementation does not work because subprocess' Popen
# object will access f.fileno and write directly to the file descriptor,
# bypassing the gzip wrapper.
#
# with gzip.open('test.gz', 'wb') as f:
#    subprocess.run(['echo', 'test'], stdout=f)
#
# This class is a workaround for the above issue.
class BackupFile:
    def __init__(self, backup_file_path: Path, compress: bool = True):
        self.backup_file_path = backup_file_path
        self.compress = compress
        self.write_fd: Optional[int] = None
        self.writer_thread: Optional[threading.Thread] = None

    def _writer_thread_fn(self, read_fd: int) -> None:
        open_fn: Any = gzip.open if self.compress else open
        with open_fn(self.backup_file_path, "wb") as backup_file:
            while data := os.read(read_fd, 4096):
                backup_file.write(data)
        os.close(read_fd)

    def __enter__(self) -> int:
        read_fd, self.write_fd = os.pipe()
        self.writer_thread = threading.Thread(target=self._writer_thread_fn, args=(read_fd,))
        self.writer_thread.start()
        return self.write_fd

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        assert self.writer_thread is not None
        assert self.write_fd is not None
        os.close(self.write_fd)
        self.writer_thread.join()
        self.write_fd = None
        self.writer_thread = None


def valid_hostname(hostname: str) -> bool:
    pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, hostname))


def valid_ip(ip_str: str) -> bool:
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False
