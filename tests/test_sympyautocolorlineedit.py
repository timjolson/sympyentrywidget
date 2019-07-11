import pytest
from sympyEntryWidget import SympyAutoColorLineEdit, unitSubs, units, UnitMisMatchException
from qt_utils.helpers_for_tests import *
from generalUtils.sympy_utils import expr_safe_check
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
    widget = SympyAutoColorLineEdit()
    show(locals())
    assert widget.getError() is None
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['blank'][0]
    assert set() == widget.getSymbols()
    assert dict() == widget.getSymbolsDict()


def test_constructor_text(qtbot):
    widget = SympyAutoColorLineEdit(text='text')
    show(locals())
    assert bool(widget.getError()) is False
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['default'][0]
    assert widget.getSymbols() == {Symbol('text')}


def test_constructor_units(qtbot):
    widget = SympyAutoColorLineEdit(text='2*mm')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['default'][0]
    assert widget.getSymbols() == set()
    assert widget.getExprUnits() == {units.mm}
    assert widget.getExprDimensions() == units.Dimension('length')


def test_constructor_expr_error(qtbot):
    for e in expr_safe_check:
        testLogger.debug(f"e = {e}")
        widget = SympyAutoColorLineEdit(text=e[0])
        show(locals())
        assert bool(widget.getError()) is e[2]
        if e[0] == '':
            assert getCurrentColor(widget.lineEdit, 'Background').names[0] == \
                   widget.defaultColors['blank'][0]
        else:
            assert getCurrentColor(widget.lineEdit, 'Background').names[0] == \
                   widget.defaultColors['error' if e[2] else 'default'][0]


def test_expr_error(qtbot):
    widget = SympyAutoColorLineEdit()
    show(locals())

    for e in expr_safe_check:
        widget.setText(e[0])
        assert bool(widget.getError()) is e[2]


def test_constructor_math(qtbot):
    widget = SympyAutoColorLineEdit(text='2*a_1 + b')
    show(locals())
    syms = widget.getSymbols()
    assert isinstance(syms.pop(), Symbol)
    assert isinstance(syms.pop(), Symbol)
    with pytest.raises(KeyError):
        syms.pop()
    syms = widget.getSymbolsDict()
    assert 'a_1' in syms.keys()
    assert 'b' in syms.keys()
    assert widget.getValue().subs({'a_1':3, 'b':2}) == 8


def test_constructor_symbol(qtbot):
    widget = SympyAutoColorLineEdit(text='word')
    show(locals())
    syms = widget.getSymbols()
    assert syms == {Symbol('word')}
    syms = widget.getSymbolsDict()
    assert 'word' in syms.keys()
    assert widget.getValue().subs({'word': 3}) == 3

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
    assert widget.getValue().subs({'word': 3, 'expon': 3}) == 24


def test_unit_consistency_good(qtbot):
    widget = SympyAutoColorLineEdit()
    for e in ['mm*3*b', 'mm*3*b + 2*yard', 'mm*3*b + 2*inch']:
        widget.setText(e)
        assert widget.getError() is False
        v = widget.getValue()
        ex = parse_expr(e, local_dict=unitSubs)
        testLogger.debug((type(v), v, type(ex), ex))
        assert v == ex


def test_unit_consistency_bad(qtbot):
    widget = SympyAutoColorLineEdit()
    for e in ['mm*3*b + 2', 'mm*3*b + 2*kg', 'mm*3*b + 2*pound', 'mm*3*b + 2*N', '1*inch + 2*mm**2']:
        testLogger.debug(f"e = {e}")
        with pytest.raises(UnitMisMatchException):
            widget.unitsAreConsistent(parse_expr(e, local_dict=unitSubs))
