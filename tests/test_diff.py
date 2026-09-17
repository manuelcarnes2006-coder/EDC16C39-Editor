"""Tests for read-only binary comparisons using synthetic temporary files."""

from edc16c39 import compare_binaries, export_diff_report, read_binary


def make_binary(tmp_path, name: str, contents: bytes):
    """Create a synthetic binary fixture and load it through the public API."""
    path = tmp_path / name
    path.write_bytes(contents)
    return read_binary(path)


def test_identical_files_have_no_differences(tmp_path):
    diff = compare_binaries(make_binary(tmp_path, "original.bin", b"\x00\x01\x02"), make_binary(tmp_path, "modified.bin", b"\x00\x01\x02"))
    assert diff.same_size is True
    assert diff.different_bytes == 0
    assert diff.differences == []
    assert diff.blocks == []


def test_reports_single_byte_and_hex_offset(tmp_path):
    diff = compare_binaries(make_binary(tmp_path, "original.bin", b"\x00\x12\x02"), make_binary(tmp_path, "modified.bin", b"\x00\x00\x02"))
    difference = diff.differences[0]
    assert (difference.offset, difference.hex_offset) == (1, "0x1")
    assert (difference.original, difference.modified) == (0x12, 0x00)


def test_groups_consecutive_changed_bytes(tmp_path):
    diff = compare_binaries(make_binary(tmp_path, "original.bin", b"\x00\x01\x02\x03\x04"), make_binary(tmp_path, "modified.bin", b"\x00\xff\xff\xff\x04"))
    assert diff.different_bytes == 3
    assert [(item.start_offset, item.end_offset) for item in diff.blocks] == [(1, 3)]
    assert diff.blocks[0].hex_range == "0x1-0x3"


def test_groups_separate_blocks(tmp_path):
    diff = compare_binaries(make_binary(tmp_path, "original.bin", b"\x00" * 10), make_binary(tmp_path, "modified.bin", b"\x00\xff\xff\x00\x00\x00\xff\x00\x00\x00"))
    assert [(item.start_offset, item.end_offset) for item in diff.blocks] == [(1, 2), (6, 6)]
    assert diff.summary()["modified_blocks"] == 2


def test_different_sizes_are_incompatible_without_byte_comparison(tmp_path):
    diff = compare_binaries(make_binary(tmp_path, "original.bin", b"\x00\x01"), make_binary(tmp_path, "modified.bin", b"\x00\x01\x02"))
    assert diff.same_size is False
    assert diff.is_compatible is False
    assert diff.differences == []
    assert "INCOMPATIBLE" in diff.text_report()


def test_summary_calculates_affected_percentage(tmp_path):
    summary = compare_binaries(make_binary(tmp_path, "original.bin", b"\x00" * 10), make_binary(tmp_path, "modified.bin", b"\xff\xff" + b"\x00" * 8)).summary()
    assert summary["different_bytes"] == 2
    assert summary["affected_percentage"] == 20.0
    assert summary["first_difference"] == "0x0"
    assert summary["last_difference"] == "0x1"


def test_exports_a_text_report(tmp_path):
    diff = compare_binaries(make_binary(tmp_path, "original.bin", b"\x00"), make_binary(tmp_path, "modified.bin", b"\xff"))
    report_path = export_diff_report(diff, tmp_path / "report.txt")
    assert report_path.read_text(encoding="utf-8") == diff.text_report()
