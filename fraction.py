from __future__ import annotations  # lets us use Fraction as a type hint inside the class

import math


class Fraction:
    __slots__ = ("_numerator", "_denominator")  # prevents adding new attributes

    def __init__(self, numerator: int, denominator: int = 1) -> None:
        # Both must be int; bool is a subclass of int, so we reject it explicitly
        for name, number in (("numerator", numerator), ("denominator", denominator)):
            if isinstance(number, bool) or not isinstance(number, int):
                raise TypeError(f"{name} must be an int, got {type(number).__name__}")
        if denominator == 0:
            raise ZeroDivisionError("denominator cannot be zero")

        # Move the sign to the numerator so the denominator is always positive
        if denominator < 0:
            numerator, denominator = -numerator, -denominator

        # Reduce to lowest terms, e.g. 2/4 -> 1/2
        divisor = math.gcd(numerator, denominator)
        self._numerator = numerator // divisor
        self._denominator = denominator // divisor

    # Properties without setters make the fraction read-only
    @property
    def numerator(self) -> int:
        return self._numerator

    @property
    def denominator(self) -> int:
        return self._denominator

    @staticmethod
    def _coerce(other: object) -> Fraction | None:
        # Turns an int into a Fraction so we can compare and calculate with ints.
        # Returns None for unsupported types.
        if isinstance(other, Fraction):
            return other
        if isinstance(other, int) and not isinstance(other, bool):
            return Fraction(other)
        return None

    def __repr__(self) -> str:
        return f"Fraction({self._numerator}, {self._denominator})"

    def __str__(self) -> str:
        if self._denominator == 1:
            return str(self._numerator)  # show 2 instead of 2/1
        return f"{self._numerator}/{self._denominator}"

    # Comparisons. NotImplemented lets Python handle unsupported types.
    def __eq__(self, other: object) -> bool:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        # Both are in lowest terms, so equal fractions have identical parts
        return (self._numerator == other._numerator
                and self._denominator == other._denominator)

    def __ne__(self, other: object) -> bool:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return not self == other

    # a/b < c/d  <=>  a*d < c*b  (exact, and valid since denominators are positive)
    def __lt__(self, other: object) -> bool:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return self._numerator * other._denominator < other._numerator * self._denominator

    def __le__(self, other: object) -> bool:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return self._numerator * other._denominator <= other._numerator * self._denominator

    def __gt__(self, other: object) -> bool:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return self._numerator * other._denominator > other._numerator * self._denominator

    def __ge__(self, other: object) -> bool:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return self._numerator * other._denominator >= other._numerator * self._denominator

    def __hash__(self) -> int:
        # Fraction(2, 1) == 2, so they must have the same hash
        if self._denominator == 1:
            return hash(self._numerator)
        return hash((self._numerator, self._denominator))

    # Arithmetic. Every operation returns a new Fraction.
    def __add__(self, other: object) -> Fraction:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return Fraction(
            self._numerator * other._denominator + other._numerator * self._denominator,
            self._denominator * other._denominator,
        )

    __radd__ = __add__  # makes 1 + Fraction(1, 2) work

    def __sub__(self, other: object) -> Fraction:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return self + (-other)

    def __rsub__(self, other: object) -> Fraction:
        # Called for e.g. 1 - Fraction(1, 2)
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return other - self

    def __mul__(self, other: object) -> Fraction:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return Fraction(self._numerator * other._numerator,
                        self._denominator * other._denominator)

    __rmul__ = __mul__  # makes 2 * Fraction(1, 3) work

    def __truediv__(self, other: object) -> Fraction:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        # Multiply by the reciprocal; dividing by zero raises ZeroDivisionError in __init__
        return Fraction(self._numerator * other._denominator,
                        self._denominator * other._numerator)

    def __rtruediv__(self, other: object) -> Fraction:
        # Called for e.g. 1 / Fraction(2, 3)
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return other / self

    def __neg__(self) -> Fraction:
        return Fraction(-self._numerator, self._denominator)

    def __abs__(self) -> Fraction:
        return Fraction(abs(self._numerator), self._denominator)

    def __float__(self) -> float:
        return self._numerator / self._denominator

    def __bool__(self) -> bool:
        return self._numerator != 0  # only 0 is False