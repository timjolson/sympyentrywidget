import pytest
from sympyentrywidget import (UnitEdit, unitSubs, units, UnitMisMatchError,
                              unitsAreConsistent, parseUnits)
from . import units_work_check
from qt_utils.helpers_for_tests import *
from qt_utils import getCurrentColor
from sympy import Symbol
from sympy.parsing.sympy_parser import parse_expr
import logging
import sys

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
testLogger = logging.getLogger('testLogger')


def test_constructor(qtbot):
    widget = UnitEdit()
    show(locals())
    assert widget.getError() is None
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['blank'][0]
    assert dict() == widget.getSymbols()


def test_constructor_text(qtbot):
    widget = UnitEdit(text='text')
    show(locals())
    assert bool(widget.getError()) is False
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['default'][0]
    assert set(widget.getSymbols().keys()) == {'text'}


def test_constructor_units(qtbot):
    widget = UnitEdit(text='2.0*mm')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['default'][0]
    assert widget.getSymbols() == dict()
    assert widget.getExpr().atoms(units.Unit) == {units.mm}
    assert widget.getDimension() == units.Dimension('length')
    assert widget.getMagnitude() == 2
    assert widget.getUnits() == units.millimeter
    assert widget.getValue() == widget.getUnits() * widget.getMagnitude()


def test_unit_consistency(qtbot):
    widget = UnitEdit()
    show(locals())

    for e in units_work_check:
        testLogger.debug(e)

        if e[1] is False:
            with pytest.raises(UnitMisMatchError):
                unitsAreConsistent(parse_expr(e[0], local_dict=unitSubs))

        widget.setText(e[0])
        assert bool(widget.getError()) is not e[1]
        if e[1] is False:
            continue


def test_conversion_with_symbols(qtbot):
    widget = UnitEdit(text='1*b*mm')
    show(locals())
    syms = widget.getSymbols()
    assert set(syms.keys()) == {'b'}

    expr = widget.getExpr()
    conv = units.convert_to(expr, units.meter)
    assert conv == units.meter * Symbol('b') / 1000
    assert widget.convertTo('meter') == conv
    assert widget.convertTo(units.meter) == conv


def test_invalid_conversion(qtbot):
    widget = UnitEdit(text='(1*mm)*b')
    show(locals())
    syms = widget.getSymbols()
    assert set(syms.keys()) == {'b'}

    assert (widget.convertTo(units.inch) - parseUnits('b*5*inch/127')).simplify() == 0
    assert (widget.convertTo('kg') - parseUnits('b*mm')).simplify() == 0
    assert (widget.convertTo(units.m*units.m) - parseUnits('b*m/1000')).simplify() == 0
    assert (widget.convertTo(units.m) - parseUnits('b*m/1000')).simplify() == 0

    widget = UnitEdit(text='2*mm')
    show(locals())
    assert widget.getSymbols() == dict()
    widget.convertTo(units.inch)

    assert (widget.convertTo('kg') - parseUnits('2*mm')).simplify() == 0
    assert (widget.convertTo(units.m*units.m) - parseUnits('1*m/500')).simplify() == 0
    assert (widget.convertTo(units.m) - parseUnits('1*m/500')).simplify() == 0
