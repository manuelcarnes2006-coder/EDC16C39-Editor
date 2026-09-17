"""Tests for the read-only ``main.py --map`` command."""

import hashlib

from edc16c39 import MapDefinition, MapReader, read_binary
from edc16c39.cli import main


def test_map_command_reads_a_definition_as_provisional_raw_uint16(tmp_path, capsys) -> None:
    binary_path = tmp_path / "sample.bin"
    contents = bytearray(0x1B18AE + 16 * 16 * 2)
    contents[0x1B18AE:0x1B18B2] = b"\x01\x00\xff\xff"
    binary_path.write_bytes(contents)
    before_hash = hashlib.sha256(contents).hexdigest()

    result = main(["--map", "1", str(binary_path)])

    captured = capsys.readouterr()
    assert result == 0
    assert "Interpretacion RAW provisional: uint16 little-endian" in captured.out
    assert "Mapa 1: Driver's Wish" in captured.out
    assert "Dimensiones: 16 x 16" in captured.out
    assert "1 65535" in captured.out
    assert hashlib.sha256(binary_path.read_bytes()).hexdigest() == before_hash


def test_validated_map_uses_its_definition_format_scale_offset_and_unit(tmp_path, capsys) -> None:
    binary_path = tmp_path / "sample.bin"
    expected_values = [
        0, 0, 300, 300, 173, 236, 359, 367, 384, 382, 384, 385, 391,
        390, 379, 373, 345, 322, 296, 283, 60, 0, 0, 0, 0,
    ]
    contents = bytearray(0x1C6960 + 25 * 2)
    contents[0x1C6960:0x1C6960 + 25 * 2] = b"".join(
        (value * 10).to_bytes(2, "big") for value in expected_values
    )
    binary_path.write_bytes(contents)

    result = main(["--map", "18", str(binary_path)])

    captured = capsys.readouterr()
    assert result == 0
    assert "Formato VALIDADO: uint16 big-endian" in captured.out
    assert "Factor: 0.1" in captured.out
    assert "Offset: 0" in captured.out
    assert "Unidad: Nm" in captured.out
    assert captured.out.split("Datos:\n", maxsplit=1)[1].splitlines() == [str(value) for value in expected_values]


def test_map_reader_applies_validated_factor_and_offset(tmp_path) -> None:
    binary_path = tmp_path / "sample.bin"
    binary_path.write_bytes(b"\x00\x0a")
    definition = MapDefinition(
        id=999,
        address=0,
        rows=1,
        columns=1,
        name="Validated test",
        category="Test",
        validated=True,
        data_type="uint16",
        endian="big",
        factor=0.5,
        offset=2,
        unit="units",
    )

    map_data = MapReader(read_binary(binary_path)).read(definition)

    assert map_data.values == ((7.0,),)
    assert map_data.unit == "units"
    assert map_data.validated is True


def test_map_command_reports_an_unknown_id(tmp_path, capsys) -> None:
    binary_path = tmp_path / "sample.bin"
    binary_path.write_bytes(b"\x00")

    result = main(["--map", "999", str(binary_path)])

    captured = capsys.readouterr()
    assert result == 1
    assert "Map ID 999 no existe" in captured.err


def test_map_command_reports_when_definition_does_not_fit_bin(tmp_path, capsys) -> None:
    binary_path = tmp_path / "sample.bin"
    binary_path.write_bytes(b"\x00")

    result = main(["--map", "1", str(binary_path)])

    captured = capsys.readouterr()
    assert result == 1
    assert "no cabe dentro del BIN" in captured.err
