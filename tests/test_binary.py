"""Tests for read-only BIN loading using synthetic temporary files."""

import hashlib

import pytest

from edc16c39.binary import TWO_MIB, BinaryFile, read_binary


def test_rejects_an_empty_file(tmp_path):
    binary_path = tmp_path / "empty.bin"
    binary_path.write_bytes(b"")

    with pytest.raises(ValueError, match="must not be empty"):
        read_binary(binary_path)


def test_reads_a_valid_binary_without_changing_it(tmp_path):
    contents = b"\x00\x01\xfe\xff"
    binary_path = tmp_path / "sample.bin"
    binary_path.write_bytes(contents)

    binary = BinaryFile(binary_path)

    assert binary.path == binary_path
    assert binary.data == contents
    assert binary.size == len(contents)
    assert binary_path.read_bytes() == contents


def test_calculates_sha256(tmp_path):
    contents = b"synthetic binary data"
    binary_path = tmp_path / "hash.bin"
    binary_path.write_bytes(contents)

    binary = read_binary(binary_path)

    assert binary.sha256 == hashlib.sha256(contents).hexdigest()


def test_identifies_an_exact_two_mib_binary(tmp_path):
    binary_path = tmp_path / "two-mib.bin"
    binary_path.write_bytes(b"\x00" * TWO_MIB)

    binary = read_binary(binary_path)

    assert binary.size == 2_097_152
    assert binary.is_2mb is True


def test_identifies_a_non_two_mib_binary(tmp_path):
    binary_path = tmp_path / "not-two-mib.bin"
    binary_path.write_bytes(b"\x00")

    assert read_binary(binary_path).is_2mb is False
