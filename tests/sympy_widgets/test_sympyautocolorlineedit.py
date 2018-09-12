import pytest
from sympyEntryWidget.sympyEntryWidget.sympy_widget import *
from generalUtils.helpers_for_tests import *
from entryWidget.utils import getCurrentColor
from sympy import Symbol
import logging
import sys

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def test_constructor(qtbot):
    widget = SympyAutoColorLineEdit()
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['blank'][0]
    syms = widget.getSymbols()
    assert syms == set()
    syms = {str(k): k for k in syms}
    assert syms == widget.getSymbolsDict()

    widget = SympyAutoColorLineEdit(startPrompt='text')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]


def test_constructor_error(qtbot):
    widget = SympyAutoColorLineEdit(startPrompt='text.')
    show(locals())
    assert widget.getError()
    assert not widget.getSymbols()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyAutoColorLineEdit(startPrompt='0.1)')
    show(locals())
    assert widget.getError()
    assert not widget.getSymbols()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyAutoColorLineEdit(startPrompt='1.)')
    show(locals())
    assert widget.getError()
    assert not widget.getSymbols()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyAutoColorLineEdit(startPrompt='1.)')
    show(locals())
    assert widget.getError()
    assert not widget.getSymbols()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyAutoColorLineEdit(startPrompt='(1.)')
    show(locals())
    assert widget.getError() is False
    assert not widget.getSymbols()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]

    widget = SympyAutoColorLineEdit(startPrompt='(.1)')
    show(locals())
    assert widget.getError() is False
    assert not widget.getSymbols()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]


def test_constructor_math(qtbot):
    widget = SympyAutoColorLineEdit(startPrompt='2*a_1 + b')
    show(locals())
    syms = widget.getSymbols()
    assert isinstance(syms.pop(), Symbol)
    assert isinstance(syms.pop(), Symbol)
    with pytest.raises(KeyError):
        syms.pop()
    syms = widget.getSymbols()
    syms = {str(k):k for k in syms}
    assert syms == widget.getSymbolsDict()
    assert isinstance(syms, dict)
    assert 'a_1' in syms.keys()
    assert 'b' in syms.keys()
    assert widget.getValue().subs({'a_1':3, 'b':2}) == 8 == widget.getExpr().subs({'a_1':3, 'b':2})


def test_constructor_symbol(qtbot):
    widget = SympyAutoColorLineEdit(startPrompt='word')
    show(locals())
    syms = widget.getSymbols()
    assert isinstance(syms.pop(), Symbol)
    with pytest.raises(KeyError):
        syms.pop()
    syms = widget.getSymbols()
    syms = {str(k): k for k in syms}
    assert syms == widget.getSymbolsDict()
    assert isinstance(syms, dict)
    assert 'word' in syms.keys()
    assert widget.getValue().subs({'word': 3}) == 3 == widget.getExpr().subs({'word': 3})

    widget.setText('word * 2**var')
    assert widget.getError()

    widget.setText('word * 2**vars')
    assert not widget.getError()

    widget.setText('word*(2**expon)')
    assert not widget.getError()

    syms = widget.getSymbols()
    assert isinstance(syms.pop(), Symbol)
    assert isinstance(syms.pop(), Symbol)
    with pytest.raises(KeyError):
        syms.pop()
    syms = widget.getSymbols()
    syms = {str(k): k for k in syms}
    assert syms == widget.getSymbolsDict()
    assert isinstance(syms, dict)
    assert 'word' in syms.keys()
    assert 'expon' in syms.keys()
    expr = widget.getExpr()
    value = widget.getValue()
    assert value.subs({'word': 3}) == expr.subs({'word': 3})
    assert value.subs({'expon': 3}) == expr.subs({'expon': 3})
    assert value.subs({'word': 3, 'expon': 3}) == 24 == expr.subs({'word': 3, 'expon': 3})


def test_expr_error(qtbot):
    widget = SympyAutoColorLineEdit()
    show(locals())

    for e in expr_safe_check:
        widget.setText(e[0])
        assert widget.hasError() is e[2]
