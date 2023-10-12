import os
import tempfile
import gzip
import threading
from fixbackup.utils import BackupFile, valid_hostname, valid_ip


def write_data(backup_fd, data):
    for _ in range(1000):
        os.write(backup_fd, data)


def test_uncompressed_writing():
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        test_data = b"test data for uncompressed writing"
        with BackupFile(temp.name, compress=False) as backup_fd:
            os.write(backup_fd, test_data)

        with open(temp.name, "rb") as f:
            read_data = f.read()

        assert test_data == read_data


def test_compressed_writing():
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        test_data = b"test data for compressed writing"
        with BackupFile(temp.name, compress=True) as backup_fd:
            os.write(backup_fd, test_data)

        with gzip.open(temp.name, "rb") as f:
            decompressed_data = f.read()

        assert test_data == decompressed_data


def test_multithreading_behavior():
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        test_data = b"test multithread"
        with BackupFile(temp.name, compress=False) as backup_fd:
            thread1 = threading.Thread(target=write_data, args=(backup_fd, test_data))
            thread2 = threading.Thread(target=write_data, args=(backup_fd, test_data))

            thread1.start()
            thread2.start()

            thread1.join()
            thread2.join()

        with open(temp.name, "rb") as f:
            read_data = f.read()

        assert len(read_data) == 2 * 1000 * len(test_data)


def test_valid_hostname():
    # Positive tests
    assert valid_hostname("some.engineering") is True
    assert valid_hostname("example.com") is True
    assert valid_hostname("sub.example.com") is True
    assert valid_hostname("subdomain.example-domain.com") is True
    assert valid_hostname("a.com") is True

    # Negative tests
    assert valid_hostname("-example.com") is False
    assert valid_hostname("example-.com") is False
    assert valid_hostname("example..com") is False
    assert valid_hostname("example.c") is False
    assert valid_hostname("example_1.com") is False

    # Edge cases
    assert valid_hostname("example") is False
    assert valid_hostname(".com") is False


def test_valid_ip():
    assert valid_ip("192.168.1.1")  # Valid IPv4
    assert valid_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334")  # Valid IPv6
    assert not valid_ip("256.256.256.256")  # Invalid IPv4
    assert not valid_ip("2001:0db8:85a3:0000:0000:8a2e:0370:GZ11")  # Invalid IPv6
    assert not valid_ip("random_string")  # Not an IP
