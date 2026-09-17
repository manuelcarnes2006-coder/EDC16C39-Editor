"""Command-line interface for safe BIN inspection and comparison."""

from __future__ import annotations

import sys
from pathlib import Path

from . import MapReader, compare_binaries, load_map_definition, read_binary


MAPS_PATH = Path(__file__).resolve().parents[2] / "definitions" / "edc16c39" / "0281015984" / "1037516790" / "maps.json"


def _format_value(value: int | float) -> str:
    """Format numeric map values without adding unvalidated precision."""
    return f"{value:g}" if isinstance(value, float) else str(value)


def _print_map(map_data) -> None:
    """Print a read-only, structured representation of extracted map data."""
    definition = map_data.definition
    print(f"ID: {definition.id}")
    print(f"Nombre: {definition.name}")
    print(f"Categoria: {definition.category}")
    print(f"Direccion: 0x{definition.address:X}")
    print(f"Dimensiones: {definition.rows} x {definition.columns}")

    if map_data.validated:
        print("Formato: VALIDADO")
        print(f"Data type: {map_data.data_type}")
        print(f"Endian: {map_data.endian}")
        print(f"Factor: {map_data.factor:g}")
        print(f"Offset: {map_data.offset:g}")
        print(f"Unidad: {map_data.unit}")
    else:
        print("Formato: RAW provisional (NO VALIDADO)")
        print(f"Data type: {map_data.data_type}")
        print(f"Endian: {map_data.endian}")
        print("Factor: no validado")
        print("Offset: no validado")
        print("Unidad: no validada")

    if definition.columns == 1:
        print("\nIndice | Valor")
        print("-------+------")
        for index, row in enumerate(map_data.values):
            print(f"{index:<6} | {_format_value(row[0])}")
        return

    print("\nDatos:")
    for row in map_data.values:
        print(" ".join(_format_value(value) for value in row))


def main(arguments: list[str] | None = None) -> int:
    """Print BIN metadata, compare BINs, or read a map without modifying a BIN."""
    arguments = sys.argv[1:] if arguments is None else arguments
    is_diff = len(arguments) == 3 and arguments[0] == "--diff"
    is_map = len(arguments) == 3 and arguments[0] == "--map"

    if not is_diff and not is_map and len(arguments) != 1:
        print('Uso: python main.py "ruta/al/archivo.bin"', file=sys.stderr)
        print('     python main.py --diff "original.bin" "modificado.bin"', file=sys.stderr)
        print('     python main.py --map <ID> "ruta/al/archivo.bin"', file=sys.stderr)
        return 2

    try:
        if is_diff:
            diff = compare_binaries(read_binary(arguments[1]), read_binary(arguments[2]))
            print(diff.text_report(), end="")
            return 0 if diff.is_compatible else 1
        if is_map:
            try:
                map_id = int(arguments[1])
            except ValueError:
                raise ValueError(f'El ID de mapa debe ser un entero: {arguments[1]!r}') from None

            binary = read_binary(arguments[2])
            definition = load_map_definition(MAPS_PATH, map_id)
            map_data = MapReader(binary).read(definition, data_type="uint16", endian="little")
            _print_map(map_data)
            return 0
        binary = read_binary(arguments[0])
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Archivo: {binary.path.name}")
    print(f"TamaÃ±o: {binary.size} bytes")
    print(f"TamaÃ±o: {binary.size / (1024 * 1024):.2f} MiB")
    print(f"SHA-256: {binary.sha256}")
    print(f"Exactamente 2 MiB: {'sÃ­' if binary.is_2mb else 'no'}")
    return 0
