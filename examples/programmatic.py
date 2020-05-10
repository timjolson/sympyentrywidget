from sympyentrywidget import SympyEntryWidget, ExprEdit, UnitEdit, DimensionEdit, SymbolEdit
from PyQt5.QtWidgets import QWidget, QVBoxLayout

# Qt stuff
# from PyQt5.Qt import QApplication  # optional, can be started from widget.mkQApp()
# from PyQt5.QtWidgets import QApplication
# app = QApplication(sys.argv)

import sys

# log to console
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# start Qt
app = SympyEntryWidget.mkQApp()

# <editor-fold desc="Support Funcs">
def show_symbols(widget):
    print(type(widget).__name__, '-> symbols:', widget.getSymbols())

def printer(title):
    return lambda *t: print(title, *t)
# </editor-fold>


w = QWidget()
layout = QVBoxLayout()

sym = SymbolEdit(text='symbol_name')
sym.hasError[object].connect(printer('SymbolEdit.hasError[object]'))
sym.exprChanged[object].connect(printer('SymbolEdit.exprChanged[object] -> Symbol is:'))
sym.setToolTip("Enter a symbol name")
layout.addWidget(sym)

expr = ExprEdit(text='1*a + 2*b - 1*a + cos(pi)')
expr.hasError[str].connect(printer('ExprEdit.hasError[str]'))
expr.exprChanged[str].connect(printer('ExprEdit.exprChanged[str] -> Expression is:'))
expr.editingFinished.connect(lambda: show_symbols(expr))
expr.editingFinished.connect(lambda: print('ExprEdit.editingFinished -> getValue():', expr.getValue()))
expr.setToolTip("Do some math")
layout.addWidget(expr)

unit = UnitEdit(text='2*mm + 1*inch')
unit.hasError[str].connect(printer('UnitEdit.hasError[str]'))
unit.exprChanged[object].connect(printer('UnitEdit.exprChanged[object]'))
unit.exprChanged.connect(lambda: print('UnitEdit.exprChanged -> getExpr()', unit.getExpr()))
unit.exprChanged.connect(lambda: print('UnitEdit.exprChanged -> getValue()', unit.getValue()))
unit.valueChanged[object].connect(printer('UnitEdit.valueChanged[object]'))
unit.setToolTip("Do math with units")
layout.addWidget(unit)

dim = DimensionEdit(text='2*mm + 1*inch', dimension='length')
dim.hasError[str].connect(printer('DimensionEdit.hasError[str]'))
dim.exprChanged[object].connect(printer('DimensionEdit.exprChanged[object]'))
dim.valueChanged[object].connect(printer('DimensionEdit.valueChanged[object]'))
dim.setToolTip("Dimension (length) is enforced")
layout.addWidget(dim)

entry = SympyEntryWidget(text='3*mm + 1*inch', windowTitle='EntryWidget', objectName='EntryWidget',
                     options='length')
entry.exprChanged[object].connect(printer('SympyEntryWidget.exprChanged[object]'))
entry.valueChanged[object].connect(printer('SympyEntryWidget.valueChanged[object]'))
entry.setToolTip("Dimension (length) is enforced")
layout.addWidget(entry)

w.setLayout(layout)
w.show()
app.exec_()
