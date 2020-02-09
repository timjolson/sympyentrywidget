import pytest
from sympyentrywidget import SympyEntryWidget, units, UnitMisMatchError, parseExpr, parseUnits, quantity_simplify
from sympy import Symbol
from qt_utils.helpers_for_tests import *
from qt_utils import getCurrentColor
from PyQt5 import QtCore
import logging, sys

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
testLogger = logging.getLogger('testLogger')


def test_constructor_blank(qtbot):
    widget = SympyEntryWidget()
    show(locals())
    testLogger.debug((widget.getError(), widget.lineEdit.getError(), widget.lineEdit._error, widget.lineEdit._expr))
    assert widget.getError() is None
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['blank'][0]


def test_constructor_text(qtbot):
    widget = SympyEntryWidget(text='text*mm')
    show(locals())
    testLogger.debug((widget.getError(), widget.lineEdit.getError(), widget.lineEdit._error, widget.lineEdit._expr))
    assert widget.getError() is False
    assert list(widget.getSymbols().keys()) == ['text']
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['default'][0]

    widget = SympyEntryWidget(text='text')
    show(locals())
    testLogger.debug((widget.getError(), widget.lineEdit.getError(), widget.lineEdit._error, widget.lineEdit._expr))
    assert widget.getError()
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['error'][0]


def test_conversion_with_symbols(qtbot):
    widget = SympyEntryWidget(text='1*b*mm', options={'mm':units.mm, 'm':units.m, 'kg':units.kg})
    show(locals())
    assert set(widget.getSymbols().keys()) == {'b'}

    expr = widget.getValue()
    conv = units.convert_to(expr, units.meter)
    assert conv == units.meter * Symbol('b') / 1000
    assert widget.convertTo('meter') == conv

    widget.setSelected('kg')
    assert widget.getError()
    assert widget.getValue() is None

    widget.setUnits('m')
    expr = widget.getValue()
    conv = units.convert_to(expr, units.gram)
    assert conv == units.meter * Symbol('b') /1000
    assert widget.convertTo('meter') == conv
    assert conv == widget.convertTo(units.gram)


def test_invalid_conversion(qtbot):
    widget = SympyEntryWidget(text='(1*mm)*b', options={'mm': units.mm, 'kg': units.kg, 'm2':units.m*units.m})
    show(locals())
    assert set(widget.getSymbols().keys()) == {'b'}

    testLogger.debug((widget.getExpr(), widget.getUnits(), widget.getValue()))
    assert widget.convertTo('kg') == parseUnits('b*mm')

    widget.setSelected('m2')
    testLogger.debug((widget.getExpr(), widget.getUnits(), widget.getValue()))
    assert bool(widget.getError()) is True

    widget.setUnits('mm')
    assert widget.convertTo('mm') == parseUnits('b*mm')


def test_text_changes_value(qtbot):
    widget = SympyEntryWidget(text='1*mm + 1*inch', options='length')
    show(locals())
    assert widget.getError() is False
    assert widget.convertTo(units.inch) == (132/127)*units.inch

    qtbot.keyPress(widget.lineEdit, QtCore.Qt.Key_Home)
    qtbot.keyClicks(widget.lineEdit, '1')
    assert widget.convertTo(units.inch) == (182/127) * units.inch
    assert quantity_simplify(widget.getValue() - (182/127 * units.inch)) == 0

    qtbot.keyPress(widget.lineEdit, 'b')
    assert widget.getError()
    assert getCurrentColor(widget.lineEdit, 'Window').names[0] == widget.defaultColors['error'][0]


def test_option_changes_value(qtbot):
    widget = SympyEntryWidget(text='3*mm', windowTitle='EntryWidget', objectName='EntryWidget',
                             options={'mm':units.mm, 'm':units.meter, 'kg':units.kg, 'n/a':units.One})
    show(locals())
    assert widget.getValue() == 3*units.mm
    widget.setUnits('kg')
    assert widget.getError()
    widget.setUnits('m')
    assert widget.getValue() == .003*units.m
    widget.setUnits('n/a')
    assert widget.getError()
    widget.setText('3')
    assert widget.getValue() == 3

    widget = SympyEntryWidget(text='3*inch', windowTitle='EntryWidget', objectName='EntryWidget',
                             options={'mm':units.mm, 'kg':units.kg, 'n/a':units.One})
    show(locals())
    assert abs(quantity_simplify(widget.getValue() - (3*25.4)*units.mm).evalf()) <= (1e-12)*units.mm
    widget.setUnits('kg')
    assert widget.getError()
    assert widget.getValue() is None
    assert widget.convertTo(units.inch) is None
    widget.setUnits('n/a')
    assert widget.getError()
    assert widget.getValue() is None
    assert widget.convertTo(units.inch) is None

    widget.setText('3*inch / (1*foot)')
    assert widget.getError() is False
    assert widget.getValue() == .25
    assert widget.convertTo(units.inch) == .25*units.inch
