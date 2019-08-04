from sympyentrywidget import SympySymbolEdit
from . import expr_safe_check
from qt_utils.helpers_for_tests import show
from qt_utils import getCurrentColor
import logging
import sys
from sympy import Symbol

from PyQt5.Qt import QApplication

app = QApplication([])

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def test_basic_constructor(qtbot):
    widget = SympySymbolEdit()
    show(locals())
    assert widget.getError()
    assert getCurrentColor(widget, 'Background').names[0] == widget.defaultColors['error'][0]
    assert widget.getExpr() is None


def test_symbol_name_error(qtbot):
    for e in expr_safe_check:
        logging.debug(e)
        widget = SympySymbolEdit(text=e[0])
        show(locals())
        assert bool(widget.getError()) is not e[3]
        if bool(widget.getError()):
            assert widget.getExpr() is None
        else:
            assert widget.getExpr() == Symbol(e[0])

    widget = SympySymbolEdit()
    for e in expr_safe_check:
        logging.debug(e)
        widget.setText(e[0])
        assert bool(widget.getError()) is not e[3]
        if bool(widget.getError()):
            assert widget.getExpr() is None
        else:
            assert widget.getExpr() == Symbol(e[0])
