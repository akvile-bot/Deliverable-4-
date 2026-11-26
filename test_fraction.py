"""Pytest tests for the Fraction class."""

import pytest

from fraction import Fraction


# ----------------------------------------------------------------------
# Initialiser
# ----------------------------------------------------------------------
def test_init_stores_numerator_and_denominator():
    f = Fraction(3, 4)
    assert f.numerator == 3
    assert f.denominator == 4


def test_default_denominator_is_one():
    f = Fraction(5)
    assert (f.numerator, f.denominator) == (5, 1)


@pytest.mark.parametrize("num, den, expected", [
    (2, 4, (1, 2)),
    (10, 5, (2, 1)),
    (0, 7, (0, 1)),
    (-6, 9, (-2, 3)),
    (100, 75, (4, 3)),
])
def test_init_reduces_to_lowest_terms(num, den, expected):
    f = Fraction(num, den)
    assert (f.numerator, f.denominator) == expected


@pytest.mark.parametrize("num, den, expected", [
    (1, -2, (-1, 2)),
    (-1, -2, (1, 2)),
    (-3, 6, (-1, 2)),
])
def test_denominator_is_always_positive(num, den, expected):
    f = Fraction(num, den)
    assert f.denominator > 0
    assert (f.numerator, f.denominator) == expected


def test_zero_denominator_raises():
    with pytest.raises(ZeroDivisionError):
        Fraction(1, 0)


@pytest.mark.parametrize("num, den", [
    (1.5, 2), (1, 2.0), ("1", 2), (1, None), (True, 2), (1, False),
])
def test_non_integer_arguments_raise(num, den):
    with pytest.raises(TypeError):
        Fraction(num, den)


@pytest.mark.parametrize("attribute", ["numerator", "denominator"])
def test_attributes_are_read_only(attribute):
    f = Fraction(1, 2)
    with pytest.raises(AttributeError):
        setattr(f, attribute, 5)


# ----------------------------------------------------------------------
# Comparisons
# ----------------------------------------------------------------------
@pytest.mark.parametrize("a, b", [
    (Fraction(1, 2), Fraction(2, 4)),
    (Fraction(-1, 3), Fraction(1, -3)),
    (Fraction(0, 5), Fraction(0, 1)),
    (Fraction(6, 3), 2),
])
def test_equal(a, b):
    assert a == b
    assert b == a
    assert not (a != b)
    assert a <= b and a >= b
    assert not (a < b) and not (a > b)


@pytest.mark.parametrize("smaller, larger", [
    (Fraction(1, 3), Fraction(1, 2)),
    (Fraction(-1, 2), Fraction(1, 3)),
    (Fraction(-3, 4), Fraction(-1, 2)),
    (Fraction(99, 100), 1),
    (0, Fraction(1, 1000)),
])
def test_ordering(smaller, larger):
    assert smaller < larger
    assert smaller <= larger
    assert larger > smaller
    assert larger >= smaller
    assert smaller != larger
    assert not (smaller > larger)
    assert not (larger <= smaller)


def test_sorting():
    fractions = [Fraction(3, 4), Fraction(-1, 2), Fraction(1, 3), Fraction(0)]
    assert sorted(fractions) == [Fraction(-1, 2), Fraction(0), Fraction(1, 3), Fraction(3, 4)]


@pytest.mark.parametrize("other", [0.5, "1/2", None])
def test_comparison_with_unsupported_type(other):
    f = Fraction(1, 2)
    assert f.__eq__(other) is NotImplemented
    assert (f == other) is False
    assert (f != other) is True
    with pytest.raises(TypeError):
        f < other


# ----------------------------------------------------------------------
# String representations
# ----------------------------------------------------------------------
@pytest.mark.parametrize("f, expected", [
    (Fraction(3, 4), "Fraction(3, 4)"),
    (Fraction(2, -4), "Fraction(-1, 2)"),
    (Fraction(5), "Fraction(5, 1)"),
])
def test_repr(f, expected):
    assert repr(f) == expected
    assert eval(repr(f)) == f


@pytest.mark.parametrize("f, expected", [
    (Fraction(3, 4), "3/4"),
    (Fraction(-1, 2), "-1/2"),
    (Fraction(4, 2), "2"),
    (Fraction(0, 3), "0"),
])
def test_str(f, expected):
    assert str(f) == expected


# ----------------------------------------------------------------------
# Arithmetic
# ----------------------------------------------------------------------
@pytest.mark.parametrize("a, b, expected", [
    (Fraction(1, 2), Fraction(1, 3), Fraction(5, 6)),
    (Fraction(1, 2), Fraction(1, 2), Fraction(1)),
    (Fraction(-1, 4), Fraction(1, 4), Fraction(0)),
    (Fraction(1, 2), 1, Fraction(3, 2)),
    (1, Fraction(1, 2), Fraction(3, 2)),
])
def test_add(a, b, expected):
    assert a + b == expected


@pytest.mark.parametrize("a, b, expected", [
    (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
    (Fraction(1, 3), Fraction(1, 2), Fraction(-1, 6)),
    (Fraction(3, 2), 1, Fraction(1, 2)),
    (1, Fraction(1, 4), Fraction(3, 4)),
])
def test_sub(a, b, expected):
    assert a - b == expected


@pytest.mark.parametrize("a, b, expected", [
    (Fraction(2, 3), Fraction(3, 4), Fraction(1, 2)),
    (Fraction(-1, 2), Fraction(1, 2), Fraction(-1, 4)),
    (Fraction(1, 3), 3, Fraction(1)),
    (2, Fraction(1, 4), Fraction(1, 2)),
])
def test_mul(a, b, expected):
    assert a * b == expected


@pytest.mark.parametrize("a, b, expected", [
    (Fraction(1, 2), Fraction(1, 4), Fraction(2)),
    (Fraction(1, 2), Fraction(-1, 4), Fraction(-2)),
    (Fraction(3, 4), 3, Fraction(1, 4)),
    (1, Fraction(2, 3), Fraction(3, 2)),
])
def test_truediv(a, b, expected):
    assert a / b == expected


def test_division_by_zero_fraction_raises():
    with pytest.raises(ZeroDivisionError):
        Fraction(1, 2) / Fraction(0)
    with pytest.raises(ZeroDivisionError):
        1 / Fraction(0)


def test_arithmetic_results_keep_invariants():
    result = Fraction(1, 6) + Fraction(1, 3) - Fraction(5, 2)
    assert result == Fraction(-2)
    assert result.denominator > 0


@pytest.mark.parametrize("operation", [
    lambda f: f + 0.5,
    lambda f: f - "1",
    lambda f: f * [1],
    lambda f: f / None,
])
def test_arithmetic_with_unsupported_type_raises(operation):
    with pytest.raises(TypeError):
        operation(Fraction(1, 2))


def test_arithmetic_does_not_change_operands():
    a, b = Fraction(1, 2), Fraction(1, 3)
    _ = a + b
    assert a == Fraction(1, 2) and b == Fraction(1, 3)


# ----------------------------------------------------------------------
# Unary operators, conversions and hashing
# ----------------------------------------------------------------------
def test_neg():
    assert -Fraction(1, 2) == Fraction(-1, 2)
    assert -Fraction(-3, 4) == Fraction(3, 4)


def test_abs():
    assert abs(Fraction(-3, 4)) == Fraction(3, 4)
    assert abs(Fraction(3, 4)) == Fraction(3, 4)


@pytest.mark.parametrize("f, expected", [
    (Fraction(1, 2), 0.5),
    (Fraction(-1, 4), -0.25),
    (Fraction(1, 3), 1 / 3),
])
def test_float(f, expected):
    assert float(f) == pytest.approx(expected)


def test_bool():
    assert bool(Fraction(1, 2))
    assert not bool(Fraction(0, 5))


def test_hash_equal_fractions_have_equal_hash():
    assert hash(Fraction(1, 2)) == hash(Fraction(2, 4))
    assert hash(Fraction(4, 2)) == hash(2)


def test_fractions_in_set_and_dict():
    assert len({Fraction(1, 2), Fraction(2, 4), Fraction(-3, -6)}) == 1
    d = {Fraction(1, 2): "half"}
    assert d[Fraction(3, 6)] == "half"
