from sympy.parsing.sympy_parser import parse_expr
from sympy import Symbol, pi
import pytest

from sympyEntryWidget import SympyEntryWidget, ComboBoxOptionSets, units, unitSubs
import logging, sys
from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
testLogger = logging.getLogger('testLogger')


def test_conversion_math():
    # just seeing what works/doesn't
    dummy_val = pi/8

    left = parse_expr("sin(2*x)")*units.centimeter
    testLogger.debug('cm: ' + str(left))
    testLogger.debug(left.atoms(Symbol))
    syms = {i.name: i for i in left.atoms(Symbol)}
    testLogger.debug(syms)

    right = parse_expr("cos(2*x)")*units.inch
    testLogger.debug('in: ' + str(right))
    testLogger.debug(right.atoms(Symbol))

    expr = left*right
    testLogger.debug('\nmultiplied')
    testLogger.debug('left*right: ' + str(expr))
    testLogger.debug('cm: ' + str(units.convert_to(expr, units.centimeter)))
    testLogger.debug('mm: ' + str(units.convert_to(expr, units.millimeter)))
    testLogger.debug('m: ' + str(units.convert_to(expr, units.meter)))
    testLogger.debug('in: ' + str(units.convert_to(expr, units.inch)))

    testLogger.debug('\nsubstitution')
    expr = units.convert_to(expr, units.mm)
    testLogger.debug('subs from syms: ' + str(expr.subs(syms['x'], dummy_val)))
    testLogger.debug('subs from str: ' + str(expr.subs('x', dummy_val)))
    testLogger.debug('subs from Symbol: ' + str(expr.subs(Symbol('x'), dummy_val)))

    testLogger.debug('\neval')
    testLogger.debug('eval from syms: ' + str(expr.subs(syms['x'], dummy_val).evalf()))
    testLogger.debug('eval from str: ' + str(expr.subs('x', dummy_val).evalf()))
    assert True


def test_string_embedded_units():
    expr1 = parse_expr("3*inch + 2*ft", evaluate=False).subs(unitSubs)
    expr2 = parse_expr("2*ft", evaluate=False).subs(unitSubs)
    expr3 = parse_expr("3*inch", evaluate=False).subs(unitSubs)

    expr1_conv = units.convert_to(expr1, units.inch)
    expr2_conv = units.convert_to(expr2, units.inch)
    expr3_conv = units.convert_to(expr3, units.inch)

    testLogger.debug('1: ' + str(expr1))
    testLogger.debug(expr1_conv)
    testLogger.debug('2: ' + str(expr2))
    testLogger.debug(expr2_conv)
    testLogger.debug('3: ' + str(expr3))
    testLogger.debug(expr3_conv)

    assert expr2_conv + expr3_conv - expr1_conv == 0
    assert expr2_conv + expr3_conv == expr1_conv
    assert expr1_conv - expr3_conv == expr2_conv
    assert expr1_conv - expr2_conv == expr3_conv

    assert units.convert_to(expr1.subs(unitSubs), units.meter) == units.convert_to(expr2 + expr3, units.meter)
    assert units.convert_to(expr1.subs(unitSubs), units.inch) == units.convert_to(expr2 + expr3, units.inch)


def test_conversion_widgets(qtbot):
    widget1 = SympyEntryWidget(text='0.5', options=ComboBoxOptionSets.length)
    widget1.setSelected('inch')
    value1 = widget1.getValue()
    testLogger.debug('val1: ' + str(value1))

    widget2 = SympyEntryWidget(text='.25', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget2.setSelected('ft')
    value2 = widget2.getValue()
    testLogger.debug('val1: ' + str(value2))

    sum_values = value1 + value2
    testLogger.debug('sum: ' + str(sum_values))

    known = 3.5 * units.inch
    evalf = units.convert_to(sum_values, widget1.units()).evalf()
    subtract = sum_values - known
    converted = units.convert_to(sum_values - known, units.inch)

    testLogger.debug('known: ' + str(known))
    testLogger.debug('evalf: ' + str(evalf))
    testLogger.debug('subtract: ' + str(subtract))
    testLogger.debug('converted: ' + str(converted))

    assert converted == 0
    assert subtract != 0
    assert str(known) == str(evalf)

    # Conversions must happen at the end :(
    assert (units.convert_to(sum_values, widget1.units()) - known) != 0


def test_conversion_widgets_2(qtbot):
    widget1 = SympyEntryWidget(text='0.5', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget1.setSelected('inch')
    value1 = widget1.getValue()

    widget2 = SympyEntryWidget(text='.25', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget2.setSelected('ft')
    value2 = widget2.getValue()

    sum_values = value1 + value2
    testLogger.debug('sum: ' + str(sum_values))

    known = 3.5 * units.inch
    evalf = units.convert_to(sum_values, widget1.units()).evalf()
    subtract = sum_values - known
    converted = units.convert_to(sum_values - known, units.inch)

    testLogger.debug('known: ' + str(known))
    testLogger.debug('evalf: ' + str(evalf))
    testLogger.debug('subtract: ' + str(subtract))
    testLogger.debug('converted: ' + str(converted))

    assert converted == 0
    with pytest.raises(AssertionError):
        assert subtract == 0
    with pytest.raises(AssertionError):
        assert subtract.evalf() == 0
    assert str(known) == str(evalf)
    assert units.convert_to(subtract.evalf(), units.inch) == 0
    assert units.convert_to(subtract, units.inch).evalf() == 0

    with pytest.raises(AssertionError):
        assert known == evalf
    with pytest.raises(AssertionError):
        assert known.evalf() == evalf.evalf()
    with pytest.raises(AssertionError):
        assert known.evalf().equals(evalf.evalf())

    # Conversions must happen at the end :(
    assert (units.convert_to(sum_values, widget1.units()) - known) != 0


def test_conversion_widgets_embedded(qtbot):
    widget1 = SympyEntryWidget(text='12.7*mm + 0.25*inch', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget1.setSelected('inch')
    value1 = widget1.getValue()

    widget2 = SympyEntryWidget(text='3*inch + 1*ft', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget2.setSelected('ft')
    value2 = widget2.getValue()

    sum_values = value1 + value2
    testLogger.debug('sum: ' + str(sum_values))

    known = 15.75 * units.inch
    evalf = sum_values.evalf()
    subtract = sum_values - known
    converted = units.convert_to(sum_values - known, units.inch)

    testLogger.debug('known: ' + str(known))
    testLogger.debug('evalf: ' + str(evalf))
    testLogger.debug('subtract: ' + str(subtract))
    testLogger.debug('converted: ' + str(converted))

    assert converted == 0
    with pytest.raises(AssertionError):
        assert subtract == 0
    with pytest.raises(AssertionError):
        assert str(known) == str(evalf)
    assert known == units.convert_to(evalf, units.inch)
    with pytest.raises(AssertionError):
        assert subtract.evalf() == 0
    assert units.convert_to(subtract.evalf(), units.inch) == 0
    assert units.convert_to(subtract, units.inch).evalf() == 0

    with pytest.raises(AssertionError):
        assert known == evalf
    with pytest.raises(AssertionError):
        assert known.evalf() == evalf.evalf()
    with pytest.raises(AssertionError):
        assert known == evalf.evalf()
    with pytest.raises(AssertionError):
        assert known.evalf() == evalf

    assert known.equals(evalf)
    assert known.equals(evalf.evalf())
    assert known.evalf().equals(evalf.evalf())
    assert known.evalf().equals(evalf)

    # Conversions must happen at the end :(
    assert (units.convert_to(sum_values, widget1.units()) - 3.75 * units.inch).equals(1 * units.foot)

    # not evaluated before comparison
    with pytest.raises(AssertionError):
        assert (units.convert_to(sum_values, widget1.units()) - 3.75 * units.inch) == (1.0 * units.foot)

    # unit mismatch
    with pytest.raises(AssertionError):
        assert (units.convert_to(sum_values, widget1.units()) - 3.75 * units.inch).evalf() == (1.0 * units.foot)

    assert units.convert_to(units.convert_to(sum_values, widget1.units()) - 3.75 * units.inch, units.foot) == (1.0 * units.foot)
    assert (units.convert_to(sum_values, widget1.units()) - 15.75 * units.inch) == 0
    assert (units.convert_to(sum_values - 15.75 * units.inch, widget1.units())) == 0

