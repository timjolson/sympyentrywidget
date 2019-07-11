from sympyEntryWidget import SympySymbolLineEdit
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
    widget = SympySymbolLineEdit()
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['error'][0]
    syms = widget.getSymbolsDict()
    assert not syms


def test_constructor_error(qtbot):
    widget = SympySymbolLineEdit(text='text')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['default'][0]
    syms = widget.getSymbolsDict()
    assert list(syms.keys()) == ['text']

    widget = SympySymbolLineEdit(text='text.')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['error'][0]

    widget = SympySymbolLineEdit(text='')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['error'][0]
    assert widget.getSymbols() == set()

    widget = SympySymbolLineEdit(text='123')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['error'][0]
    assert widget.getSymbols() == set()

    widget = SympySymbolLineEdit(text='2*a_1 + b')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['error'][0]
    assert widget.getSymbols() == set()


def test_symbol_name_error(qtbot):
    widget = SympySymbolLineEdit()
    for e in expr_safe_check:
        logging.debug(e)
        widget.setText(e[0])
        assert bool(widget.getError()) is not e[3]
