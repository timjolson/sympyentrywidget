from sympyEntryWidget.sympyEntryWidget.sympy_widget import *
import logging
import sys

from PyQt5.Qt import QApplication


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = QApplication([])

w = SympyEntryWidget(startPrompt='text')
w.show()
app.exec_()

w = SympyEntryWidget(startPrompt='text.')
w.show()
app.exec_()

def show_symbols(widget):
    print(widget.getSymbols())

w = SympyEntryWidget(startPrompt='text.', onEditingFinished=show_symbols)
w.show()
app.exec_()
