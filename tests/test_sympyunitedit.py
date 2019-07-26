import pytest
from sympyentrywidget import SympyUnitEdit, unitSubs, units, UnitMisMatchException, expr_safe_check
from qt_utils.helpers_for_tests import *
from qt_utils import getCurrentColor
from sympy import Symbol
from sympy.parsing.sympy_parser import parse_expr
import logging
import sys

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG-1)
testLogger = logging.getLogger('testLogger')


def test_constructor(qtbot):
    widget = SympyUnitEdit()
    show(locals())
    assert widget.getError() is None
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['blank'][0]
    assert set() == widget.getSymbols()
    assert dict() == widget.getSymbolsDict()


def test_constructor_text(qtbot):
    widget = SympyUnitEdit(text='text')
    show(locals())
    assert bool(widget.getError()) is False
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['default'][0]
    assert widget.getSymbols() == {Symbol('text')}


def test_constructor_math(qtbot):
    widget = SympyUnitEdit(text='2*a_1 + b')
    show(locals())
    syms = widget.getSymbols()
    assert isinstance(syms.pop(), Symbol)
    assert isinstance(syms.pop(), Symbol)
    with pytest.raises(KeyError):
        syms.pop()
    syms = widget.getSymbolsDict()
    assert 'a_1' in syms.keys()
    assert 'b' in syms.keys()
    assert widget.getExpr().subs({'a_1':3, 'b':2}) == 8


def test_constructor_symbol(qtbot):
    widget = SympyUnitEdit(text='word')
    show(locals())
    syms = widget.getSymbols()
    assert syms == {Symbol('word')}
    syms = widget.getSymbolsDict()
    assert 'word' in syms.keys()
    assert widget.getExpr().subs({'word': 3}) == 3

    # 'var' is a function somewhere in sympy
    widget.setText('word * 2**var')
    assert bool(widget.getError()) is True

    # but 'vars' is not
    widget.setText('word * 2**vars')
    assert widget.getError() is False

    widget.setText('word*(2**expon)')
    assert widget.getError() is False

    syms = widget.getSymbols()
    assert 2 == len(syms)
    assert all(isinstance(s, Symbol) for s in syms)
    syms = widget.getSymbolsDict()
    assert 'word' in syms.keys()
    assert 'expon' in syms.keys()
    assert widget.getExpr().subs({'word': 3, 'expon': 3}) == 24


def test_constructor_units(qtbot):
    widget = SympyUnitEdit(text='2*mm')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['default'][0]
    assert widget.getSymbols() == set()
    assert widget.getExpr().atoms(units.Unit) == {units.mm}
    assert widget.getExprDimensions() == units.Dimension('length')


def test_unit_consistency_good(qtbot):
    widget = SympyUnitEdit()
    for e in ['mm*3', 'mm*3 + 2*yard', 'mm*3 + 2*inch']:
        testLogger.debug(e)
        widget.setText(e)
        assert widget.getError() is False
        v = widget.getExpr()
        ex = parse_expr(e, local_dict=unitSubs)
        testLogger.debug((type(v), v, type(ex), ex))
        assert abs(widget.getExpr() - ex).simplify() < units.inch*1e-15
        assert widget.getExpr() - ex == 0
        assert abs(widget.getValue() - ex).simplify() < units.inch*1e-15
        assert widget.getValue() - ex == 0

        assert abs(widget.getExpr() - ex) < units.inch*1e-15
        assert widget.getExpr() - ex == 0
        assert abs(widget.getValue() - ex) < units.inch*1e-15
        assert widget.getValue() - ex == 0


def test_unit_consistency_bad(qtbot):
    widget = SympyUnitEdit()
    for e in ['2 + 3*mm', 'mm*3 + 2', 'mm*3 + 2*kg', '1*inch + 2*mm**2']:
        testLogger.debug(f"e = {e}")
        with pytest.raises(UnitMisMatchException):
            widget.unitsAreConsistent(parse_expr(e, local_dict=unitSubs))


def test_conversion_with_symbols(qtbot):
    widget = SympyUnitEdit(text='(1*a)*b*mm')
    assert widget.getSymbols() == {Symbol('a'), Symbol('b')}

    expr = widget.getExpr()
    conv = units.convert_to(expr, units.meter)
    assert conv == units.meter * Symbol('a') * Symbol('b') / 1000
    assert widget.convertTo('meter') == conv
    assert widget.convertTo(units.meter) == conv


def test_invalid_conversion(qtbot):
    widget = SympyUnitEdit(text='(1*mm*a)*b')
    assert widget.getSymbols() == {Symbol('a'), Symbol('b')}

    testLogger.debug(widget.getExpr())
    with pytest.raises(UnitMisMatchException):
        widget.convertTo('kg')

    with pytest.raises(UnitMisMatchException):
        widget.convertTo(units.m*units.m)
