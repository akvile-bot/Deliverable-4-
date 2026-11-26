"""A simple Fraction class with integer numerator and positive denominator."""

from __future__ import annotations

import math


class Fraction:
    """An immutable fraction numerator/denominator.

    The fraction is always stored in lowest terms with a strictly positive
    denominator. A negative sign is moved to the numerator, so
    ``Fraction(1, -2)`` is stored as -1/2.
    """

    __slots__ = ("_numerator", "_denominator")

    def __init__(self, numerator: int, denominator: int = 1) -> None:
        for name, number in (("numerator", numerator), ("denominator", denominator)):
            if isinstance(number, bool) or not isinstance(number, int):
                raise TypeError(f"{name} must be an int, got {type(number).__name__}")
        if denominator == 0:
            raise ZeroDivisionError("denominator cannot be zero")

        if denominator < 0:  # keep the denominator strictly positive
            numerator, denominator = -numerator, -denominator

        divisor = math.gcd(numerator, denominator)
        self._numerator = numerator // divisor
        self._denominator = denominator // divisor

    # ------------------------------------------------------------------
    # Read-only attributes
    # ------------------------------------------------------------------
    @property
    def numerator(self) -> int:
        return self._numerator

    @property
    def denominator(self) -> int:
        return self._denominator

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    @staticmethod
    def _coerce(other: object) -> Fraction | None:
        """Turn an int into a Fraction; return None for unsupported types."""
        if isinstance(other, Fraction):
            return other
        if isinstance(other, int) and not isinstance(other, bool):
            return Fraction(other)
        return None

    # ------------------------------------------------------------------
    # String representations
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"Fraction({self._numerator}, {self._denominator})"

    def __str__(self) -> str:
        if self._denominator == 1:
            return str(self._numerator)
        return f"{self._numerator}/{self._denominator}"

    # ------------------------------------------------------------------
    # Comparisons (exact, using cross-multiplication; denominators > 0)
    # ------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return (self._numerator == other._numerator
                and self._denominator == other._denominator)

    def __ne__(self, other: object) -> bool:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return not self == other

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
        # Equal values must have equal hashes, also Fraction(2, 1) == 2.
        if self._denominator == 1:
            return hash(self._numerator)
        return hash((self._numerator, self._denominator))

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------
    def __add__(self, other: object) -> Fraction:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return Fraction(
            self._numerator * other._denominator + other._numerator * self._denominator,
            self._denominator * other._denominator,
        )

    __radd__ = __add__  # addition is commutative: 1 + Fraction(1, 2)

    def __sub__(self, other: object) -> Fraction:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return self + (-other)

    def __rsub__(self, other: object) -> Fraction:
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

    __rmul__ = __mul__  # multiplication is commutative: 2 * Fraction(1, 3)

    def __truediv__(self, other: object) -> Fraction:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        # Fraction() raises ZeroDivisionError if other is zero.
        return Fraction(self._numerator * other._denominator,
                        self._denominator * other._numerator)

    def __rtruediv__(self, other: object) -> Fraction:
        other = self._coerce(other)
        if other is None:
            return NotImplemented
        return other / self

    # ------------------------------------------------------------------
    # Unary operators and conversions
    # ------------------------------------------------------------------
    def __neg__(self) -> Fraction:
        return Fraction(-self._numerator, self._denominator)

    def __abs__(self) -> Fraction:
        return Fraction(abs(self._numerator), self._denominator)

    def __float__(self) -> float:
        return self._numerator / self._denominator

    def __bool__(self) -> bool:
        return self._numerator != 0
