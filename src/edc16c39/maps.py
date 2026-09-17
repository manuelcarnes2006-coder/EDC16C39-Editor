"""Read-only extraction of validated and provisional EDC16C39 maps."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .binary import BinaryFile


@dataclass(frozen=True)
class MapDefinition:
    """The location and shape of one map declared in ``maps.json``."""

    id: int
    address: int
    rows: int
    columns: int
    name: str
    category: str
    validated: bool
    data_type: str | None = None
    endian: str | None = None
    factor: float | None = None
    offset: float | None = None
    unit: str | None = None

    @classmethod
    def from_mapping(cls, definition: dict[str, object]) -> "MapDefinition":
        """Create a definition from an entry in the supplied JSON database."""
        return cls(
            id=int(definition["id"]),
            address=int(str(definition["address"]), 16),
            rows=int(definition["rows"]),
            columns=int(definition["columns"]),
            name=str(definition["name"]),
            category=str(definition["category"]),
            validated=bool(definition["validated"]),
            data_type=str(definition["data_type"]) if "data_type" in definition else None,
            endian=str(definition["endian"]) if "endian" in definition else None,
            factor=float(definition["factor"]) if "factor" in definition else None,
            offset=float(definition["offset"]) if "offset" in definition else None,
            unit=str(definition["unit"]) if "unit" in definition else None,
        )


@dataclass(frozen=True)
class MapData:
    """A map extracted from a BIN, with its applicable format metadata."""

    definition: MapDefinition
    values: tuple[tuple[int | float, ...], ...]
    data_type: str
    endian: str
    factor: float
    offset: float
    unit: str | None
    validated: bool


def load_map_definition(maps_path: str | Path, map_id: int) -> MapDefinition:
    """Load *map_id* from a user-supplied map-definition database."""
    definitions = json.loads(Path(maps_path).read_text(encoding="utf-8"))
    for definition in definitions:
        if int(definition["id"]) == map_id:
            return MapDefinition.from_mapping(definition)
    raise ValueError(f"Map ID {map_id} no existe en la base de definiciones.")


class MapReader:
    """Extract map cells from a :class:`BinaryFile` without modifying it."""

    def __init__(self, binary: BinaryFile) -> None:
        self.binary = binary

    def read(
        self,
        definition: MapDefinition,
        *,
        data_type: str | None = None,
        endian: str | None = None,
    ) -> MapData:
        """Read a map in row-major order, validating that it fits in the BIN."""
        if definition.validated:
            if None in (definition.data_type, definition.endian, definition.factor, definition.offset, definition.unit):
                raise ValueError(f"El mapa validado ID {definition.id} no tiene un formato completo.")
            data_type = definition.data_type
            endian = definition.endian
            factor = definition.factor
            offset = definition.offset
            unit = definition.unit
        else:
            data_type = data_type or "uint16"
            endian = endian or "little"
            factor = 1.0
            offset = 0.0
            unit = None

        if data_type != "uint16":
            raise ValueError(f"Unsupported data type: {data_type}")
        if endian not in {"little", "big"}:
            raise ValueError(f"Unsupported byte order: {endian}")

        byte_count = definition.rows * definition.columns * 2
        end_offset = definition.address + byte_count
        if end_offset > self.binary.size:
            raise ValueError(
                f"El mapa ID {definition.id} no cabe dentro del BIN: requiere "
                f"0x{definition.address:X}-0x{end_offset - 1:X}, pero el BIN termina en "
                f"0x{self.binary.size - 1:X}."
            )

        raw = self.binary.data[definition.address:end_offset]
        cells = [int.from_bytes(raw[index:index + 2], endian) for index in range(0, len(raw), 2)]
        values = [cell * factor + offset for cell in cells]
        if factor == 1 and offset == 0:
            values = cells
        rows = tuple(
            tuple(values[row * definition.columns:(row + 1) * definition.columns])
            for row in range(definition.rows)
        )
        return MapData(definition, rows, data_type, endian, factor, offset, unit, definition.validated)
