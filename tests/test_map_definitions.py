"""Validation for the user-provided EDC16C39 map database."""

import json
from pathlib import Path


MAPS_PATH = Path(__file__).parents[1] / "definitions" / "edc16c39" / "0281015984" / "1037516790" / "maps.json"


def load_maps() -> list[dict[str, object]]:
    """Load the static map definition database."""
    return json.loads(MAPS_PATH.read_text(encoding="utf-8"))


def test_map_database_contains_exactly_100_entries() -> None:
    """The supplied database has one consecutive identifier per map."""
    maps = load_maps()
    assert len(maps) == 100
    assert [item["id"] for item in maps] == list(range(1, 101))


def test_map_addresses_are_unique_and_valid_hexadecimal() -> None:
    """Each map address is a unique hexadecimal BIN offset."""
    addresses = [item["address"] for item in load_maps()]
    assert len(addresses) == len(set(addresses))
    assert all(isinstance(address, str) and address.startswith("0x") for address in addresses)
    for address in addresses:
        int(address, 16)


def test_map_dimensions_are_positive_integers() -> None:
    """Rows and columns preserve the supplied positive dimensions."""
    for item in load_maps():
        assert isinstance(item["rows"], int) and item["rows"] > 0
        assert isinstance(item["columns"], int) and item["columns"] > 0


def test_only_maps_18_and_19_are_validated() -> None:
    """Maps 18 and 19 are the sole experimentally validated definitions so far."""
    for item in load_maps():
        assert item["source"] == "EDCMasterHP user-provided definition"
        assert item["validated"] is (item["id"] in {18, 19})


def test_map_18_has_the_validated_raw_format() -> None:
    """The experimentally verified Torque Limiter format remains explicit."""
    map_18 = next(item for item in load_maps() if item["id"] == 18)

    assert map_18 == {
        "id": 18,
        "address": "0x1C6960",
        "rows": 25,
        "columns": 1,
        "name": "Torque Limiter",
        "category": "Torque Limiter",
        "source": "EDCMasterHP user-provided definition",
        "validated": True,
        "data_type": "uint16",
        "endian": "big",
        "factor": 0.1,
        "offset": 0,
        "unit": "Nm",
    }


def test_map_19_has_the_validated_raw_format() -> None:
    """The experimentally verified second Torque Limiter format remains explicit."""
    map_19 = next(item for item in load_maps() if item["id"] == 19)

    assert map_19 == {
        "id": 19,
        "address": "0x1C6A92",
        "rows": 25,
        "columns": 1,
        "name": "Torque Limiter",
        "category": "Torque Limiter",
        "source": "EDCMasterHP user-provided definition",
        "validated": True,
        "data_type": "uint16",
        "endian": "big",
        "factor": 0.1,
        "offset": 0,
        "unit": "Nm",
    }
