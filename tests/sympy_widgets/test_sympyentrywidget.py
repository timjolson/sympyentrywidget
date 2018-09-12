import pytest
from sympyEntryWidget.sympyEntryWidget.sympy_widget import *
from generalUtils.helpers_for_tests import *
from entryWidget.utils import getCurrentColor
from sympy import Symbol
import logging, sys

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def test_constructor(qtbot):
    widget = SympyEntryWidget()
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['blank'][0]
    syms = widget.getSymbols()
    assert syms == set()
    syms = {str(k): k for k in syms}
    assert syms == widget.getSymbolsDict()

    widget = SympyEntryWidget(startPrompt='text')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]


def test_constructor_error(qtbot):
    widget = SympyEntryWidget(startPrompt='text.')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyEntryWidget(startPrompt='0.1)')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyEntryWidget(startPrompt='1.)')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyEntryWidget(startPrompt='1.)')
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['error'][0]

    widget = SympyEntryWidget(startPrompt='(1.)')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]

    widget = SympyEntryWidget(startPrompt='(.1)')
    show(locals())
    assert widget.getError() is False
    assert getCurrentColor(widget._editBox, 'Background')[0][0] == widget.defaultColors['default'][0]


def test_constructor_math(qtbot):
    widget = SympyEntryWidget(startPrompt='2*a_1 + b')
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
    assert str(widget.getValue().subs({'a_1':3, 'b':2})) == '8*opt1'


def test_conversion(qtbot):
    widget = SympyEntryWidget(startPrompt='(1*a)*b', options=['mm', 'kg'])
    syms = widget.getSymbolsDict()
    assert len(syms) == 2
    assert all([s in syms.keys() for s in ['a', 'b']])

    expr = widget.getValue()
    assert str(expr.subs({'millimeter': 'test'})) == 'test*a*b'
    assert units.convert_to(expr, getattr(units, 'meter')) == units.convert_to(expr, units.meter)
    assert widget.convert_to('meter') == units.convert_to(expr, getattr(units, 'meter'))

    widget.setSelected('kg')
    syms = widget.getSymbolsDict()
    assert len(syms) == 2
    assert all([s in syms.keys() for s in ['a', 'b']])

    expr = widget.getValue()
    assert str(expr.subs({'kilogram': 'test'})) == 'test*a*b'
    assert units.convert_to(expr, getattr(units, 'gram')) == units.convert_to(expr, units.gram)
    assert widget.convert_to('gram') == units.convert_to(expr, getattr(units, 'gram'))
    assert widget.convert_to('gram') == widget.convert_to(units.gram)

