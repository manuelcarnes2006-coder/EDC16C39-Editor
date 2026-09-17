"""Read-only comparison tools for loaded binary files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .binary import BinaryFile


@dataclass(frozen=True, slots=True)
class ByteDifference:
    """One changed byte at an offset shared by two compatible binaries."""

    offset: int
    hex_offset: str
    original: int
    modified: int


@dataclass(frozen=True, slots=True)
class DifferenceBlock:
    """An inclusive range containing consecutive changed bytes."""

    start_offset: int
    end_offset: int

    @property
    def size(self) -> int:
        """Return the number of bytes in this inclusive range."""
        return self.end_offset - self.start_offset + 1

    @property
    def hex_range(self) -> str:
        """Return the range formatted for display in hexadecimal."""
        return f"0x{self.start_offset:X}-0x{self.end_offset:X}"


class BinaryDiff:
    """The read-only result of comparing two :class:`BinaryFile` objects."""

    def __init__(self, original: BinaryFile, modified: BinaryFile) -> None:
        """Compare compatible files, or mark a size mismatch as incompatible."""
        self.original_size: int = original.size
        self.modified_size: int = modified.size
        self.same_size: bool = self.original_size == self.modified_size
        self.is_compatible: bool = self.same_size
        self.differences: list[ByteDifference] = []

        if self.same_size:
            self.differences = [
                ByteDifference(offset, f"0x{offset:X}", old, new)
                for offset, (old, new) in enumerate(zip(original.data, modified.data, strict=True))
                if old != new
            ]
        self.blocks: list[DifferenceBlock] = self._group_consecutive_differences()

    @property
    def different_bytes(self) -> int:
        """Return the total number of changed bytes, or zero if incompatible."""
        return len(self.differences)

    @property
    def total_different_bytes(self) -> int:
        """Alias for :attr:`different_bytes` suitable for reports."""
        return self.different_bytes

    def _group_consecutive_differences(self) -> list[DifferenceBlock]:
        """Group changed offsets into inclusive consecutive ranges."""
        if not self.differences:
            return []
        blocks: list[DifferenceBlock] = []
        start = end = self.differences[0].offset
        for difference in self.differences[1:]:
            if difference.offset == end + 1:
                end = difference.offset
            else:
                blocks.append(DifferenceBlock(start, end))
                start = end = difference.offset
        blocks.append(DifferenceBlock(start, end))
        return blocks

    def summary(self) -> dict[str, int | float | str | None | bool]:
        """Return concise metrics for display or serialization."""
        percentage = self.different_bytes / self.original_size * 100 if self.same_size else 0.0
        return {
            "compatible": self.is_compatible,
            "different_bytes": self.different_bytes,
            "affected_percentage": percentage,
            "first_difference": self.differences[0].hex_offset if self.differences else None,
            "last_difference": self.differences[-1].hex_offset if self.differences else None,
            "modified_blocks": len(self.blocks),
        }

    def text_report(self) -> str:
        """Build a human-readable, non-mutating comparison report."""
        lines = ["Informe de comparación BIN", f"Tamaño original: {self.original_size} bytes", f"Tamaño modificado: {self.modified_size} bytes"]
        if not self.is_compatible:
            return "\n".join(lines + ["Resultado: INCOMPATIBLE (los tamaños son distintos)", "No se realizó comparación byte a byte."]) + "\n"
        info = self.summary()
        lines += ["Resultado: compatible", f"Bytes diferentes: {info['different_bytes']}", f"Porcentaje afectado: {info['affected_percentage']:.2f}%", f"Primera diferencia: {info['first_difference'] or 'ninguna'}", f"Última diferencia: {info['last_difference'] or 'ninguna'}", f"Bloques consecutivos modificados: {info['modified_blocks']}", "Bloques modificados:"]
        lines.extend(f"- {block.hex_range} ({block.size} bytes)" for block in self.blocks)
        if not self.blocks:
            lines.append("- ninguno")
        return "\n".join(lines) + "\n"


def compare_binaries(original: BinaryFile, modified: BinaryFile) -> BinaryDiff:
    """Compare two loaded binaries without writing to either source file."""
    return BinaryDiff(original, modified)


def export_diff_report(diff: BinaryDiff, path: str | Path) -> Path:
    """Write the text report to *path* and return its path."""
    report_path = Path(path)
    report_path.write_text(diff.text_report(), encoding="utf-8")
    return report_path
