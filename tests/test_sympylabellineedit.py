import pytest
from sympyEntryWidget import SympyLabelLineEdit
from qt_utils.helpers_for_tests import *
from qt_utils.helpers_for_qt_tests import *
from qt_utils import getCurrentColor
from . import *
import logging
import sys
from sympy import Symbol

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def test_basic_constructor(qtbot):
    widget = SympyLabelLineEdit()
    show(locals())
    assert widget.getError() is None
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['blank'][0]
    assert widget.getSymbols() == set()

    widget = SympyLabelLineEdit(text='text')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['default'][0]
    assert widget.getSymbols() == {Symbol('text')}


def test_constructor_label(qtbot):
    widget = SympyLabelLineEdit(label=test_strings[1])
    show(locals())
    assert widget.getLabel() == test_strings[1]
    assert widget.label.text() == test_strings[1]


def test_setlabel(qtbot):
    widget = SympyLabelLineEdit(label=test_strings[1])
    show(locals())

    widget.setLabel(test_strings[2])
    assert widget.getLabel() == test_strings[2]
    assert widget.label.text() == test_strings[2]
