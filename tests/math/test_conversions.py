from sympy.parsing.sympy_parser import parse_expr
from sympy import Symbol, pi
import pytest

from sympyEntryWidget.sympy_widget import *
import logging, sys
from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


#TODO: rewrite this test file for clarity
def test_conversion_math():
    # just seeing what works/doesn't
    dummy_val = pi/8

    left = parse_expr("sin(2*x)")*units.centimeter
    logging.debug('cm: ' + str(left))
    logging.debug(left.atoms(Symbol))
    syms = {i.name: i for i in left.atoms(Symbol)}

    right = parse_expr("cos(2*x)")*units.inch
    logging.debug('in: ' + str(right))
    logging.debug(right.atoms(Symbol))

    expr = left*right
    logging.debug('\nmultiplied')
    logging.debug('left*right: ' + str(expr))
    logging.debug('cm: ' + str(units.convert_to(expr, units.centimeter)))
    logging.debug('mm: ' + str(units.convert_to(expr, units.millimeter)))
    logging.debug('m: ' + str(units.convert_to(expr, units.meter)))
    logging.debug('in: ' + str(units.convert_to(expr, units.inch)))

    logging.debug('\nsubstitution')
    expr = units.convert_to(expr, units.mm)
    logging.debug('subs from syms: ' + str(expr.subs(syms['x'], dummy_val)))
    logging.debug('subs from str: ' + str(expr.subs('x', dummy_val)))
    logging.debug('subs from Symbol: ' + str(expr.subs(Symbol('x'), dummy_val)))

    logging.debug('\neval')
    logging.debug('eval from syms: ' + str(expr.subs(syms['x'], dummy_val).evalf()))
    logging.debug('eval from str: ' + str(expr.subs('x', dummy_val).evalf()))
    assert True


def test_string_embedded_units():
    expr1 = parse_expr("3*inch + 2*ft", evaluate=False).subs(unitSubs)
    expr2 = parse_expr("2*ft", evaluate=False).subs(unitSubs)
    expr3 = parse_expr("3*inch", evaluate=False).subs(unitSubs)

    expr1_conv = units.convert_to(expr1, units.inch)
    expr2_conv = units.convert_to(expr2, units.inch)
    expr3_conv = units.convert_to(expr3, units.inch)

    logging.debug('1: ' + str(expr1))
    logging.debug(expr1_conv)
    logging.debug('2: ' + str(expr2))
    logging.debug(expr2_conv)
    logging.debug('3: ' + str(expr3))
    logging.debug(expr3_conv)

    assert expr2_conv + expr3_conv - expr1_conv == 0
    assert expr2_conv + expr3_conv == expr1_conv
    assert expr1_conv - expr3_conv == expr2_conv
    assert expr1_conv - expr2_conv == expr3_conv

    assert units.convert_to(expr1.subs(unitSubs), units.meter) == units.convert_to(expr2 + expr3, units.meter)
    assert units.convert_to(expr1.subs(unitSubs), units.inch) == units.convert_to(expr2 + expr3, units.inch)


def test_conversion_widgets(qtbot):
    widget1 = SympyEntryWidget(startPrompt='0.5', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget1.setSelected('inch')
    value1 = widget1.getValue()
    logging.debug('val1: ' + str(value1))

    widget2 = SympyEntryWidget(startPrompt='.25', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget2.setSelected('ft')
    value2 = widget2.getValue()
    logging.debug('val1: ' + str(value2))

    sum_values = value1 + value2
    logging.debug('sum: ' + str(sum_values))

    known = 3.5 * units.inch
    evalf = units.convert_to(sum_values, widget1.getUnits()).evalf()
    subtract = sum_values - known
    converted = units.convert_to(sum_values - known, units.inch)

    logging.debug('known: ' + str(known))
    logging.debug('evalf: ' + str(evalf))
    logging.debug('subtract: ' + str(subtract))
    logging.debug('converted: ' + str(converted))

    assert converted == 0
    assert subtract != 0
    assert str(known) == str(evalf)

    # Conversions must happen at the end :(
    assert (units.convert_to(sum_values, widget1.getUnits()) - known) != 0


def test_conversion_widgets_2(qtbot):
    widget1 = SympyEntryWidget(startPrompt='0.5', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget1.setSelected('inch')
    value1 = widget1.getValue()

    widget2 = SympyEntryWidget(startPrompt='.25', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget2.setSelected('ft')
    value2 = widget2.getValue()

    sum_values = value1 + value2
    logging.debug('sum: ' + str(sum_values))

    known = 3.5 * units.inch
    evalf = units.convert_to(sum_values, widget1.getUnits()).evalf()
    subtract = sum_values - known
    converted = units.convert_to(sum_values - known, units.inch)

    logging.debug('known: ' + str(known))
    logging.debug('evalf: ' + str(evalf))
    logging.debug('subtract: ' + str(subtract))
    logging.debug('converted: ' + str(converted))

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
    assert (units.convert_to(sum_values, widget1.getUnits()) - known) != 0


def test_conversion_widgets_embedded(qtbot):
    widget1 = SympyEntryWidget(startPrompt='12.7*mm + 0.25*inch', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget1.setSelected('inch')
    value1 = widget1.getValue()

    widget2 = SympyEntryWidget(startPrompt='3*inch + 1*ft', options=['mm', 'inch', 'm', 'cm', 'ft'])
    widget2.setSelected('ft')
    value2 = widget2.getValue()

    sum_values = value1 + value2
    logging.debug('sum: ' + str(sum_values))

    known = 15.75 * units.inch
    evalf = sum_values.evalf()
    subtract = sum_values - known
    converted = units.convert_to(sum_values - known, units.inch)

    logging.debug('known: ' + str(known))
    logging.debug('evalf: ' + str(evalf))
    logging.debug('subtract: ' + str(subtract))
    logging.debug('converted: ' + str(converted))

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
    assert (units.convert_to(sum_values, widget1.getUnits()) - 3.75*units.inch).equals(1*units.foot)

    # not evaluated before comparison
    with pytest.raises(AssertionError):
        assert (units.convert_to(sum_values, widget1.getUnits()) - 3.75*units.inch) == (1.0*units.foot)

    # unit mismatch
    with pytest.raises(AssertionError):
        assert (units.convert_to(sum_values, widget1.getUnits()) - 3.75*units.inch).evalf() == (1.0*units.foot)

    assert units.convert_to(units.convert_to(sum_values, widget1.getUnits()) - 3.75*units.inch, units.foot) == (1.0*units.foot)
    assert (units.convert_to(sum_values, widget1.getUnits()) - 15.75*units.inch) == 0
    assert (units.convert_to(sum_values - 15.75*units.inch, widget1.getUnits())) == 0


def test_symbols_contain_units():
    # test groups of symbols
    from sympy import Symbol
    from sympy.abc import a
    from sympy.physics.units import inch, meter, kilogram, newton, mm, kg

    assert symbolsContainUnits({a, inch}) is True
    assert symbolsContainUnits({a, meter}) is True
    assert symbolsContainUnits({a, mm}) is True
    assert symbolsContainUnits({a, kg}) is True
    assert symbolsContainUnits({a, kilogram}) is True
    assert symbolsContainUnits({a, newton}) is True

    assert symbolsContainUnits({a, Symbol('newton')}) is True
    assert symbolsContainUnits({Symbol('madeup_unit')}) is False
    assert symbolsContainUnits({a, 'madeup_unit'}) is False
    assert symbolsContainUnits({a, 'mm'}) is True
    assert symbolsContainUnits({a, 'newton'}) is True
    assert symbolsContainUnits({a, 'kg'}) is True

    assert symbolsContainUnits({}) is False
    assert symbolsContainUnits({a}) is False


if __name__ == '__main__':
    test_conversion_math()
