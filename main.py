"""Command-line entry point for safe BIN inspection and comparison."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from edc16c39 import compare_binaries, read_binary


def main(arguments: list[str] | None = None) -> int:
    """Print BIN metadata or compare two BIN files without modifying them."""
    arguments = sys.argv[1:] if arguments is None else arguments
    is_diff = len(arguments) == 3 and arguments[0] == "--diff"

    if not is_diff and len(arguments) != 1:
        print('Uso: python main.py "ruta/al/archivo.bin"', file=sys.stderr)
        print('     python main.py --diff "original.bin" "modificado.bin"', file=sys.stderr)
        return 2

    try:
        if is_diff:
            diff = compare_binaries(read_binary(arguments[1]), read_binary(arguments[2]))
            print(diff.text_report(), end="")
            return 0 if diff.is_compatible else 1
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
