"""Pytest tests for the Temperature class."""

import pytest

from temperature import Temperature

TOL = 1e-9


# ----------------------------------------------------------------------
# 1. Initialization
# ----------------------------------------------------------------------
def test_default_unit_is_celsius():
    t = Temperature(25)
    assert t.unit == "C"
    assert t.value == 25.0


@pytest.mark.parametrize("unit, expected", [
    ("c", "C"), ("C", "C"),
    ("f", "F"), ("F", "F"),
    ("k", "K"), ("K", "K"),
])
def test_units_are_case_insensitive(unit, expected):
    assert Temperature(300, unit).unit == expected


def test_value_is_stored_as_float():
    assert isinstance(Temperature(25, "C").value, float)


@pytest.mark.parametrize("attribute", ["value", "unit"])
def test_attributes_are_read_only(attribute):
    t = Temperature(25, "C")
    with pytest.raises(AttributeError):
        setattr(t, attribute, 30)


def test_cannot_add_new_attributes():
    t = Temperature(25, "C")
    with pytest.raises(AttributeError):
        t.new_attribute = 1


# ----------------------------------------------------------------------
# 2. Validation
# ----------------------------------------------------------------------
@pytest.mark.parametrize("bad_unit", ["X", "", "Celsius", "kelvin", "CF", None, 1])
def test_invalid_unit_raises(bad_unit):
    with pytest.raises(ValueError):
        Temperature(10, bad_unit)


@pytest.mark.parametrize("value, unit", [
    (-273.16, "C"),
    (-459.68, "F"),
    (-0.01, "K"),
    (-1000, "C"),
])
def test_below_absolute_zero_raises(value, unit):
    with pytest.raises(ValueError):
        Temperature(value, unit)


@pytest.mark.parametrize("value, unit", [(-273.15, "C"), (-459.67, "F"), (0, "K")])
def test_exactly_absolute_zero_is_allowed(value, unit):
    Temperature(value, unit)  # should not raise


@pytest.mark.parametrize("bad_value", ["25", None, [25], True])
def test_non_numeric_value_raises(bad_value):
    with pytest.raises(TypeError):
        Temperature(bad_value, "C")


def test_convert_to_invalid_unit_raises():
    with pytest.raises(ValueError):
        Temperature(25, "C").convert_to("X")


# ----------------------------------------------------------------------
# 3. Conversions at reference points
# ----------------------------------------------------------------------
REFERENCE_POINTS = [
    pytest.param(-273.15, -459.67, 0.0, id="absolute_zero"),
    pytest.param(-40.0, -40.0, 233.15, id="C_F_crossover"),
    pytest.param(0.0, 32.0, 273.15, id="water_freezes"),
    pytest.param(37.0, 98.6, 310.15, id="body_temperature"),
    pytest.param(100.0, 212.0, 373.15, id="water_boils"),
]


@pytest.mark.parametrize("c, f, k", REFERENCE_POINTS)
def test_conversions_from_celsius(c, f, k):
    t = Temperature(c, "C")
    assert t.to_celsius() == pytest.approx(c, abs=TOL)
    assert t.to_fahrenheit() == pytest.approx(f, abs=TOL)
    assert t.to_kelvin() == pytest.approx(k, abs=TOL)


@pytest.mark.parametrize("c, f, k", REFERENCE_POINTS)
def test_conversions_from_fahrenheit(c, f, k):
    t = Temperature(f, "F")
    assert t.to_celsius() == pytest.approx(c, abs=TOL)
    assert t.to_fahrenheit() == pytest.approx(f, abs=TOL)
    assert t.to_kelvin() == pytest.approx(k, abs=TOL)


@pytest.mark.parametrize("c, f, k", REFERENCE_POINTS)
def test_conversions_from_kelvin(c, f, k):
    t = Temperature(k, "K")
    assert t.to_celsius() == pytest.approx(c, abs=TOL)
    assert t.to_fahrenheit() == pytest.approx(f, abs=TOL)
    assert t.to_kelvin() == pytest.approx(k, abs=TOL)


@pytest.mark.parametrize("target", ["c", "F", "k"])
def test_convert_to_returns_new_temperature(target):
    original = Temperature(100, "C")
    converted = original.convert_to(target)
    assert isinstance(converted, Temperature)
    assert converted is not original
    assert converted.unit == target.upper()
    assert converted == original          # same physical temperature
    assert original.unit == "C"           # original unchanged


# ----------------------------------------------------------------------
# 4. Round-trip conversions
# ----------------------------------------------------------------------
@pytest.mark.parametrize("celsius", [-273.15, -40, 0, 21.5, 37, 100, 1234.5678])
def test_round_trip_c_f_k_c(celsius):
    original = Temperature(celsius, "C")
    result = original.convert_to("F").convert_to("K").convert_to("C")
    assert result.unit == "C"
    assert result.value == pytest.approx(original.value, abs=TOL)
    assert result == original


# ----------------------------------------------------------------------
# 5. Cross-unit comparisons
# ----------------------------------------------------------------------
@pytest.mark.parametrize("a, b", [
    (Temperature(0, "C"), Temperature(32, "F")),
    (Temperature(0, "C"), Temperature(273.15, "K")),
    (Temperature(-40, "C"), Temperature(-40, "F")),
    (Temperature(100, "C"), Temperature(373.15, "K")),
    (Temperature(212, "F"), Temperature(373.15, "K")),
])
def test_equality_across_units(a, b):
    assert a == b
    assert b == a
    assert not (a != b)
    assert a <= b and a >= b
    assert not (a < b) and not (a > b)


def test_equality_uses_tolerance():
    assert Temperature(0, "C") == Temperature(1e-10, "C")
    assert Temperature(0, "C") != Temperature(1e-8, "C")


@pytest.mark.parametrize("colder, warmer", [
    (Temperature(0, "C"), Temperature(33, "F")),
    (Temperature(30, "F"), Temperature(0, "C")),
    (Temperature(273, "K"), Temperature(0, "C")),
    (Temperature(-41, "C"), Temperature(-40, "F")),
    (Temperature(99, "C"), Temperature(373.15, "K")),
])
def test_ordering_across_units(colder, warmer):
    assert colder < warmer
    assert colder <= warmer
    assert warmer > colder
    assert warmer >= colder
    assert colder != warmer
    assert not (colder > warmer)
    assert not (warmer < colder)


def test_sorting_mixed_units():
    temps = [Temperature(100, "C"), Temperature(0, "K"), Temperature(50, "F")]
    assert [t.unit for t in sorted(temps)] == ["K", "F", "C"]


@pytest.mark.parametrize("other", [0, 25.0, "25 C", None])
def test_comparison_with_non_temperature(other):
    t = Temperature(25, "C")
    assert t.__eq__(other) is NotImplemented
    assert t.__lt__(other) is NotImplemented
    assert (t == other) is False
    assert (t != other) is True
    with pytest.raises(TypeError):
        t < other


# ----------------------------------------------------------------------
# 6. Formatting
# ----------------------------------------------------------------------
@pytest.mark.parametrize("temp, expected", [
    (Temperature(25, "C"), "25.00 °C"),
    (Temperature(98.6, "f"), "98.60 °F"),
    (Temperature(273.15, "K"), "273.15 K"),
    (Temperature(-40.126, "C"), "-40.13 °C"),
])
def test_str(temp, expected):
    assert str(temp) == expected


@pytest.mark.parametrize("temp, expected", [
    (Temperature(25, "C"), "Temperature(25.0, 'C')"),
    (Temperature(98.6, "f"), "Temperature(98.6, 'F')"),
    (Temperature(0, "K"), "Temperature(0.0, 'K')"),
])
def test_repr(temp, expected):
    assert repr(temp) == expected


def test_repr_can_recreate_object():
    t = Temperature(36.6, "C")
    assert eval(repr(t)) == t
