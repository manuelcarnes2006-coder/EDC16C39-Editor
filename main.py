"""Command-line entry point for safe BIN metadata inspection."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from edc16c39 import read_binary


def main(arguments: list[str] | None = None) -> int:
    """Print basic metadata for a BIN file without modifying it."""
    arguments = sys.argv[1:] if arguments is None else arguments

    if len(arguments) != 1:
        print('Uso: python main.py "ruta/al/archivo.bin"', file=sys.stderr)
        return 2

    try:
        binary = read_binary(arguments[0])
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Archivo: {binary.path.name}")
    print(f"Tamaño: {binary.size} bytes")
    print(f"Tamaño: {binary.size / (1024 * 1024):.2f} MiB")
    print(f"SHA-256: {binary.sha256}")
    print(f"Exactamente 2 MiB: {'sí' if binary.is_2mb else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
