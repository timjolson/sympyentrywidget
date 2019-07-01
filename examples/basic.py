from sympyEntryWidget import SympyEntryWidget
import logging
import sys

from PyQt5.Qt import QApplication

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = QApplication([])

w = SympyEntryWidget(text='text')
w.show()
app.exec_()

w = SympyEntryWidget(text='text.')
w.show()
app.exec_()


def show_symbols(widget):
    print(widget.getSymbols())


w = SympyEntryWidget(text='text.')
w.editingFinished.connect(lambda: show_symbols(w))
w.show()
app.exec_()
