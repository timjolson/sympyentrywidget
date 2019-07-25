from sympyentrywidget import SympyEntryWidget, SympyExprEdit, SympyUnitEdit, SympySymbolEdit
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import logging
import sys

from PyQt5.Qt import QApplication

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG-1)

app = QApplication([])
w = QWidget()
layout = QVBoxLayout()

def show_symbols(widget):
    print('symbols:', widget.getSymbols())

def printer(title):
    return lambda *t: print(title, *t)


sym = SympySymbolEdit(text='text', windowTitle='SymbolEdit', objectName='SymbolEdit')
sym.hasError[object].connect(printer('hasError[object]'))
sym.exprChanged[object].connect(printer('Symbol is:'))
layout.addWidget(sym)

expr = SympyExprEdit(text='text', windowTitle='ExprEdit', objectName='ExprEdit')
expr.hasError[str].connect(printer('hasError[str]'))
expr.exprChanged[str].connect(printer('Expression is:'))
expr.editingFinished.connect(lambda: show_symbols(expr))
layout.addWidget(expr)

unit = SympyUnitEdit(text='text', windowTitle='UnitEdit', objectName='UnitEdit')
unit.hasError[str].connect(printer('hasError[str]'))
unit.exprChanged[object].connect(lambda o: print('exprChanged[object]', o.evalf()))
unit.exprChanged.connect(lambda: print('exprChanged', unit.getValue()))
layout.addWidget(unit)

# entry = SympyEntryWidget(text='3*mm + 1*inch', windowTitle='EntryWidget', objectName='EntryWidget',
#                      options='length')
# entry.valueChanged[object].connect(printer('valueChanged[object]'))
# layout.addWidget(entry)
w.setLayout(layout)
w.show()
app.exec_()
