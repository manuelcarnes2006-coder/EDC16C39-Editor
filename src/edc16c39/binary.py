"""Safe, read-only loading of binary files."""

from __future__ import annotations

import hashlib
from pathlib import Path


TWO_MIB = 2 * 1024 * 1024


class BinaryFile:
    """An immutable-in-practice snapshot of a binary file read from disk.

    The source file is opened only in binary read mode and is never written to
    by this class.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

        if not self.path.exists():
            raise FileNotFoundError(f"Binary file does not exist: {self.path}")
        if not self.path.is_file():
            raise ValueError(f"Binary path is not a file: {self.path}")

        with self.path.open("rb") as binary_file:
            self.data = binary_file.read()

        self.size = len(self.data)
        if not isinstance(self.size, int) or self.size <= 0:
            raise ValueError("Binary file must not be empty")

        self.sha256 = hashlib.sha256(self.data).hexdigest()

    @property
    def is_2mb(self) -> bool:
        """Whether the file is exactly 2 MiB (2,097,152 bytes)."""
        return self.size == TWO_MIB


def read_binary(path: str | Path) -> BinaryFile:
    """Load *path* as a :class:`BinaryFile` without modifying it."""
    return BinaryFile(path)
