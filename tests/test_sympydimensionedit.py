import pytest
from sympyentrywidget import DimensionEdit, units
from PyQt5 import QtCore
from qt_utils.helpers_for_tests import *
import logging
import sys

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
testLogger = logging.getLogger('testLogger')


def test_constructor(qtbot):
    widget = DimensionEdit()
    show(locals())
    assert widget.getDimension() == units.length
    assert widget.dimension == 'length'


def test_constructor_text(qtbot):
    widget = DimensionEdit(text='text', dimension='force')
    show(locals())
    assert widget.dimension == 'force'
    assert widget.getDimension() == units.force


def test_constructor_units(qtbot):
    widget = DimensionEdit(text='2*mm')
    show(locals())
    assert widget.getDimension() == units.length
    assert widget.dimension == 'length'


def test_set_dimension(qtbot):
    widget = DimensionEdit(text='2*mm')
    show(locals())
    assert widget.getDimension() == units.length
    assert widget.dimension == 'length'

    widget.setDimension('force')
    assert widget.getDimension() == units.force
    assert widget.dimension == 'force'
    assert widget.getError()
    widget.setText('2*lbf')
    assert widget.getError() is False
    widget.setDimension(units.Dimension('length'))
    assert widget.getError()
    widget.setText('sin(3*pi)')
    assert widget.getError()
    qtbot.keyClicks(widget, '*mm')
    assert widget.getError() is False

