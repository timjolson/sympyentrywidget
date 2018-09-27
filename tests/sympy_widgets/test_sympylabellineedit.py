import pytest
from sympyEntryWidget.sympy_widget import *
from generalUtils.helpers_for_tests import *
from generalUtils import getCurrentColor
from sympy import Symbol
import logging, sys

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#TODO: review tests for redundancy

def test_constructor(qtbot):
    widget = SympyLabelLineEdit()
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['blank'][0]
    syms = widget.getSymbols()
    assert syms == set()
    syms = {str(k): k for k in syms}
    assert syms == widget.getSymbolsDict()

    widget = SympyLabelLineEdit(startPrompt='text')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]


def test_constructor_label(qtbot):
    widget = SympyLabelLineEdit(label=test_strings[1])
    show(locals())
    assert widget.getLabel() == test_strings[1]

    assert widget.getLabel() == test_strings[1]
    assert widget._label.text() == test_strings[1]


def test_constructor_error(qtbot):
    widget = SympyLabelLineEdit(startPrompt='text.')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyLabelLineEdit(startPrompt='0.1)')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyLabelLineEdit(startPrompt='1.)')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyLabelLineEdit(startPrompt='1.)')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyLabelLineEdit(startPrompt='(1.)')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]

    widget = SympyLabelLineEdit(startPrompt='(.1)')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]


def test_constructor_math(qtbot):
    widget = SympyLabelLineEdit(startPrompt='2*a_1 + b')
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
    assert widget.getValue().subs({'a_1':3, 'b':2}) == 8
