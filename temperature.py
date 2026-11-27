from __future__ import annotations  # lets us use Temperature as a type hint inside the class


class Temperature:
    VALID_UNITS = ("C", "F", "K")
    TOLERANCE = 1e-9  # used for all floating-point comparisons

    __slots__ = ("_value", "_unit")  # prevents adding new attributes to an instance

    def __init__(self, value: float, unit: str = "C") -> None:
        # bool is a subclass of int, so we reject it explicitly
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"value must be a number, got {type(value).__name__}")

        self._unit = self._validate_unit(unit)
        self._value = float(value)

        # Check in Kelvin; the tolerance allows tiny rounding errors at absolute zero
        if self.to_kelvin() < -self.TOLERANCE:
            raise ValueError(f"{self._value} {self._unit} is below absolute zero (0 K)")

    @classmethod
    def _validate_unit(cls, unit: str) -> str:
        # Accept "c", "f", "k" as well, and always store the unit in upper case
        if not isinstance(unit, str) or unit.upper() not in cls.VALID_UNITS:
            raise ValueError(f"Invalid unit {unit!r}; expected one of {cls.VALID_UNITS}")
        return unit.upper()

    # Properties without setters make value and unit read-only
    @property
    def value(self) -> float:
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

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
        target = self._validate_unit(target_unit)
        converters = {"C": self.to_celsius, "F": self.to_fahrenheit, "K": self.to_kelvin}
        # Returns a new object, so the original is never changed
        return Temperature(converters[target](), target)

    def __repr__(self) -> str:
        return f"Temperature({self._value!r}, '{self._unit}')"

    def __str__(self) -> str:
        # Kelvin is written without the degree sign (SI convention)
        symbol = "K" if self._unit == "K" else f"°{self._unit}"
        return f"{self._value:.2f} {symbol}"

    # All comparisons convert to Kelvin, so different units can be compared.
    # NotImplemented lets Python handle comparisons with other types.
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
        # Must be smaller by more than the tolerance, otherwise they count as equal
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

    # Equality with a tolerance can't be matched by a hash, so the class is unhashable
    __hash__ = None
