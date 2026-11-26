"""Temperature class supporting Celsius ("C"), Fahrenheit ("F") and Kelvin ("K")."""

from __future__ import annotations


class Temperature:
    """An immutable temperature value with a unit.

    All comparisons are done in Kelvin with an absolute tolerance of 1e-9,
    so temperatures given in different units can be compared directly.
    """

    VALID_UNITS = ("C", "F", "K")
    TOLERANCE = 1e-9

    __slots__ = ("_value", "_unit")

    def __init__(self, value: float, unit: str = "C") -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"value must be a number, got {type(value).__name__}")

        self._unit = self._validate_unit(unit)
        self._value = float(value)

        if self.to_kelvin() < -self.TOLERANCE:
            raise ValueError(
                f"{self._value} {self._unit} is below absolute zero (0 K)"
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @classmethod
    def _validate_unit(cls, unit: str) -> str:
        """Return the unit in upper case, or raise ValueError if it is invalid."""
        if not isinstance(unit, str) or unit.upper() not in cls.VALID_UNITS:
            raise ValueError(
                f"Invalid unit {unit!r}; expected one of {cls.VALID_UNITS}"
            )
        return unit.upper()

    # ------------------------------------------------------------------
    # Read-only attributes
    # ------------------------------------------------------------------
    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

    # ------------------------------------------------------------------
    # Conversions
    # ------------------------------------------------------------------
    def to_celsius(self) -> float:
        if self._unit == "C":
            return self._value
        if self._unit == "K":
            return self._value - 273.15
        return (self._value - 32) * 5 / 9  # from Fahrenheit

    def to_fahrenheit(self) -> float:
        if self._unit == "F":
            return self._value
        if self._unit == "C":
            return self._value * 9 / 5 + 32
        return (self._value - 273.15) * 9 / 5 + 32  # from Kelvin

    def to_kelvin(self) -> float:
        if self._unit == "K":
            return self._value
        if self._unit == "C":
            return self._value + 273.15
        return (self._value - 32) * 5 / 9 + 273.15  # from Fahrenheit

    def convert_to(self, target_unit: str) -> Temperature:
        """Return a new Temperature expressed in ``target_unit``."""
        target = self._validate_unit(target_unit)
        converters = {
            "C": self.to_celsius,
            "F": self.to_fahrenheit,
            "K": self.to_kelvin,
        }
        return Temperature(converters[target](), target)

    # ------------------------------------------------------------------
    # String representations
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"Temperature({self._value!r}, '{self._unit}')"

    def __str__(self) -> str:
        # Kelvin is an absolute scale and is written without the degree sign.
        symbol = "K" if self._unit == "K" else f"°{self._unit}"
        return f"{self._value:.2f} {symbol}"

    # ------------------------------------------------------------------
    # Comparisons (done in Kelvin, with tolerance)
    # ------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return abs(self.to_kelvin() - other.to_kelvin()) <= self.TOLERANCE

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return not self == other

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.to_kelvin() < other.to_kelvin() - self.TOLERANCE

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self < other or self == other

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.to_kelvin() > other.to_kelvin() + self.TOLERANCE

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Temperature):
            return NotImplemented
        return self > other or self == other

    # Equality uses a tolerance, so equal objects could get different hashes.
    # Temperature objects are therefore deliberately unhashable.
    __hash__ = None
