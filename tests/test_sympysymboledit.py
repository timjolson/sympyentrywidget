from sympyentrywidget import SympySymbolEdit
from qt_utils.helpers_for_tests import *
from generalUtils.sympy_utils import *
from qt_utils import getCurrentColor
import logging
import sys
from sympy import Symbol

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#TODO: review tests for redundancy


def test_basic_constructor(qtbot):
    widget = SympySymbolEdit()
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['error'][0]
    syms = widget.getExpr()
    assert syms is None


def test_constructor_error(qtbot):
    widget = SympySymbolEdit(text='text')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['default'][0]
    syms = widget.getExpr()
    assert syms == Symbol('text')

    widget = SympySymbolEdit(text='text.')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['error'][0]
    assert widget.getExpr() is None

    widget = SympySymbolEdit(text='')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['error'][0]
    assert widget.getExpr() is None

    widget = SympySymbolEdit(text='123')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['error'][0]
    assert widget.getExpr() is None

    widget = SympySymbolEdit(text='2*a_1 + b')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['error'][0]
    assert widget.getExpr() is None


def test_symbol_name_error(qtbot):
    widget = SympySymbolEdit()
    for e in expr_safe_check:
        logging.debug(e)
        widget.setText(e[0])
        assert bool(widget.getError()) is not e[3]
        if bool(widget.getError()):
            assert widget.getExpr() is None
        else:
            assert widget.getExpr() == Symbol(e[0])
