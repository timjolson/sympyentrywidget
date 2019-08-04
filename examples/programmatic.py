from sympyentrywidget import SympyEntryWidget, SympyExprEdit, SympyUnitEdit, SympySymbolEdit
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


sym = SympySymbolEdit(text='symbol_name')
sym.hasError[object].connect(printer('SympySymbolEdit.hasError[object]'))
sym.exprChanged[object].connect(printer('SympySymbolEdit.exprChanged[object] -> Symbol is:'))
layout.addWidget(sym)

expr = SympyExprEdit(text='1*a + 2*b - 1*a + cos(pi)')
expr.hasError[str].connect(printer('SympyExprEdit.hasError[str]'))
expr.exprChanged[str].connect(printer('SympyExprEdit.exprChanged[str] -> Expression is:'))
expr.editingFinished.connect(lambda: show_symbols(expr))
expr.editingFinished.connect(lambda: print('SympyExprEdit.editingFinished -> getValue():', expr.getValue()))
layout.addWidget(expr)

unit = SympyUnitEdit(text='2*mm + 1*inch')
unit.hasError[str].connect(printer('SympyUnitEdit.hasError[str]'))
unit.exprChanged[object].connect(printer('SympyUnitEdit.exprChanged[object]'))
unit.exprChanged.connect(lambda: print('SympyUnitEdit.exprChanged -> getExpr()', unit.getExpr()))
unit.exprChanged.connect(lambda: print('SympyUnitEdit.exprChanged -> getValue()', unit.getValue()))
unit.valueChanged[object].connect(printer('SympyUnitEdit.valueChanged[object]'))
layout.addWidget(unit)

entry = SympyEntryWidget(text='3*mm + 1*inch', windowTitle='EntryWidget', objectName='EntryWidget',
                     options='length')
entry.exprChanged[object].connect(printer('SympyEntryWidget.exprChanged[object]'))
entry.valueChanged[object].connect(printer('SympyEntryWidget.valueChanged[object]'))
layout.addWidget(entry)

w.setLayout(layout)
w.show()
app.exec_()
