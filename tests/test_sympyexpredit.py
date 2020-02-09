import pytest
from sympyentrywidget import ExprEdit, parseExpr
from . import expr_safe_check
from qt_utils.helpers_for_tests import *
from qt_utils import getCurrentColor
from sympy import Symbol
import logging
import sys

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
testLogger = logging.getLogger('testLogger')


def test_constructor(qtbot):
    widget = ExprEdit()
    show(locals())
    assert widget.getError() is None
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['blank'][0]
    assert dict() == widget.getSymbols()


def test_constructor_text(qtbot):
    widget = ExprEdit(text='text')
    show(locals())
    assert bool(widget.getError()) is False
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['default'][0]
    assert list(widget.getSymbols().values()) == [Symbol('text')]


def test_expr_error(qtbot):
    for e in expr_safe_check:
        testLogger.debug(f"e = {e}")
        widget = ExprEdit(text=e[0])
        show(locals())
        assert bool(widget.getError()) is e[2]
        if e[0] == '':
            assert getCurrentColor(widget, 'Background').names[0] == \
                   widget.defaultColors['blank'][0]
        else:
            assert getCurrentColor(widget, 'Background').names[0] == \
                   widget.defaultColors['error' if e[2] else 'default'][0]

    widget = ExprEdit()
    show(locals())
    for e in expr_safe_check:
        widget.setText(e[0])
        assert bool(widget.getError()) is e[2]
        if e[0] == '':
            assert getCurrentColor(widget, 'Background').names[0] == \
                   widget.defaultColors['blank'][0]
        else:
            assert getCurrentColor(widget, 'Background').names[0] == \
                   widget.defaultColors['error' if e[2] else 'default'][0]


def test_constructor_math(qtbot):
    widget = ExprEdit(text='2*a_1 + b')
    show(locals())
    syms = widget.getSymbols()
    assert set(syms.keys()) == {'a_1', 'b'}
    assert widget.getExpr().subs({'a_1':3, 'b':2}) == 8


def test_constructor_symbols(qtbot):
    widget = ExprEdit(text='word')
    show(locals())
    syms = widget.getSymbols()
    assert set(syms.keys()) == {'word'}
    assert widget.getExpr().subs({'word': 3}) == 3

    # 'var' is a function somewhere in sympy
    widget.setText('word * 2**var')
    assert bool(widget.getError()) is True

    # but 'vars' is not
    widget.setText('sin(word) * 2**vars')
    assert widget.getError() is False

    widget.setText('sin(word)*(2**expon)')
    assert widget.getError() is False

    assert set(widget.getSymbols().keys()) == {'word', 'expon'}
    assert widget.getExpr().subs({'word': parseExpr('pi/2'), 'expon': 3}) == 8


def test_basic_math(qtbot):
    widget = ExprEdit(text='2*cos(pi) + 20/5')
    show(locals())
    assert widget.getSymbols() == dict()
    assert widget.getExpr() == 2
    assert widget.getValue() == 2

    widget = ExprEdit(text='2*cos(pi) + pi')
    show(locals())
    assert widget.getSymbols() == dict()
    assert widget.getExpr() == parseExpr('-2 + pi')
    assert widget.getExpr() != parseExpr('-2 + pi').evalf()
    assert widget.getValue() == parseExpr('-2 + pi').evalf()

