from sympyEntryWidget.sympy_widget import *
from generalUtils.helpers_for_tests import *
from generalUtils.sympy_utils import *
from generalUtils.qt_utils import getCurrentColor
import logging
import sys

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#TODO: review tests for redundancy

def test_basic_constructor(qtbot):
    widget = SympySymbolLineEdit()
    show(locals())
    assert widget.hasError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]
    syms = widget.getSymbolsDict()
    assert list(syms.keys()) == ['variableName']


def test_constructor_error(qtbot):
    widget = SympySymbolLineEdit(startPrompt='text')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]
    syms = widget.getSymbolsDict()
    assert list(syms.keys()) == ['text']

    widget = SympySymbolLineEdit(startPrompt='text.')
    show(locals())
    assert widget.hasError()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympySymbolLineEdit(startPrompt='')
    show(locals())
    assert widget.hasError() is True
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]
    assert widget.getSymbols() == set()

    widget = SympySymbolLineEdit(startPrompt='123')
    show(locals())
    assert widget.text() == '123'
    assert widget.hasError() is True
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]
    assert widget.getSymbols() == set()


def test_symbol_name_error(qtbot):
    widget = SympySymbolLineEdit()
    for e in expr_safe_check:
        logging.debug(e)
        widget.setText(e[0])
        assert widget.hasError() is not e[3]


def test_constructor_math(qtbot):
    widget = SympySymbolLineEdit(startPrompt='2*a_1 + b')
    show(locals())
    syms = widget.getSymbols()
    assert syms == set()

