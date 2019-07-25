import pytest
from sympyentrywidget import SympyEntryWidget, units, UnitMisMatchException
from sympy import Symbol
from qt_utils.helpers_for_tests import *
from qt_utils import getCurrentColor
import logging, sys

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG-1)
testLogger = logging.getLogger('testLogger')


def test_constructor_blank(qtbot):
    widget = SympyEntryWidget()
    show(locals())
    assert widget.getError() is None
    assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['blank'][0]


def test_constructor_text(qtbot):
    widget = SympyEntryWidget(text='text')
    show(locals())
    assert widget.getError() is False
    # assert widget.getSymbols() == {Symbol('text')}
    # assert getCurrentColor(widget.lineEdit, 'Background').names[0] == widget.defaultColors['default'][0]


def test_conversion_with_symbols(qtbot):
    widget = SympyEntryWidget(text='(1*a)*b', options={'mm':units.mm, 'kg':units.kg})
    assert widget.getSymbols() == {Symbol('a'), Symbol('b')}

    expr = widget.getValue()
    conv = units.convert_to(expr, units.meter)
    assert conv == units.meter * Symbol('a') * Symbol('b') / 1000
    assert widget.convertTo('meter') == conv


def test_conversion_with_symbols_and_subs(qtbot):
    widget = SympyEntryWidget(text='(1*a)*b', options={'mm': units.mm, 'kg': units.kg})
    widget.setSelected('kg')
    assert widget.getSymbols() == {Symbol('a'), Symbol('b')}

    expr = widget.getValue()
    conv = units.convert_to(expr, units.gram)
    assert conv == units.gram * 1000 * Symbol('a') * Symbol('b')
    assert widget.convertTo('gram') == conv
    assert conv == widget.convertTo(units.gram)


def test_invalid_conversion(qtbot):
    widget = SympyEntryWidget(text='(1*mm*a)*b', options={'mm': units.mm, 'kg': units.kg, 'm2':units.m*units.m})
    assert widget.getSymbols() == {Symbol('a'), Symbol('b')}

    testLogger.debug((widget.getExpr(), widget.getUnits(), widget.getValue()))
    with pytest.raises(UnitMisMatchException):
        widget.convertTo('kg')

    widget.setSelected('m2')
    testLogger.debug((widget.getExpr(), widget.getUnits(), widget.getValue()))

    assert bool(widget.getError()) is True

    with pytest.raises(UnitMisMatchException):
        widget.convertTo('mm')
