from sympyentrywidget import SympyEntryWidget, ExprEdit, UnitEdit, DimensionEdit, SymbolEdit
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import logging
import sys

from PyQt5.Qt import QApplication

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = QApplication([])
w = QWidget()
layout = QVBoxLayout()

def show_symbols(widget):
    print(type(widget).__name__, '-> symbols:', widget.getSymbols())

def printer(title):
    return lambda *t: print(title, *t)


sym = SymbolEdit(text='symbol_name')
sym.hasError[object].connect(printer('SymbolEdit.hasError[object]'))
sym.exprChanged[object].connect(printer('SymbolEdit.exprChanged[object] -> Symbol is:'))
layout.addWidget(sym)

expr = ExprEdit(text='1*a + 2*b - 1*a + cos(pi)')
expr.hasError[str].connect(printer('ExprEdit.hasError[str]'))
expr.exprChanged[str].connect(printer('ExprEdit.exprChanged[str] -> Expression is:'))
expr.editingFinished.connect(lambda: show_symbols(expr))
expr.editingFinished.connect(lambda: print('ExprEdit.editingFinished -> getValue():', expr.getValue()))
layout.addWidget(expr)

unit = UnitEdit(text='2*mm + 1*inch')
unit.hasError[str].connect(printer('UnitEdit.hasError[str]'))
unit.exprChanged[object].connect(printer('UnitEdit.exprChanged[object]'))
unit.exprChanged.connect(lambda: print('UnitEdit.exprChanged -> getExpr()', unit.getExpr()))
unit.exprChanged.connect(lambda: print('UnitEdit.exprChanged -> getValue()', unit.getValue()))
unit.valueChanged[object].connect(printer('UnitEdit.valueChanged[object]'))
layout.addWidget(unit)

dim = DimensionEdit(text='2*mm + 1*inch', dimension='length')
dim.hasError[str].connect(printer('DimensionEdit.hasError[str]'))
dim.exprChanged[object].connect(printer('DimensionEdit.exprChanged[object]'))
dim.valueChanged[object].connect(printer('DimensionEdit.valueChanged[object]'))
layout.addWidget(dim)

entry = SympyEntryWidget(text='3*mm + 1*inch', windowTitle='EntryWidget', objectName='EntryWidget',
                     options='length')
entry.exprChanged[object].connect(printer('SympyEntryWidget.exprChanged[object]'))
entry.valueChanged[object].connect(printer('SympyEntryWidget.valueChanged[object]'))
layout.addWidget(entry)

w.setLayout(layout)
w.show()
app.exec_()
