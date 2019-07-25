from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.Qt import QApplication
from PyQt5 import QtCore  # for mouse click events
from qt_utils.colors import rgb

from entrywidget import AutoColorLineEdit, LabelLineEdit, EntryWidget
from sympyentrywidget import (SympyExprEdit, SympySymbolEdit,
                              SympyLabelEdit, SympyEntryWidget, ComboBoxOptionSets)

import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


##################
# helper functions, read their doc strings for reference
def check_error_typed(widget):
    """Returns 'ERROR' if widget.text() == 'error', False otherwise"""
    if widget.text() == 'error':
        widget.logger.info('ERROR')
        return 'ERROR'
    return False

def change_label_on_typing(widget):
    """Uses widget.setLabel() to change the QLabel to widget.text()"""
    widget.logger.info('change label to: ' + widget.text())
    widget.setLabel(widget.text())

def change_label_to_result(widget):
    """Sets widget label to the result of the expression."""
    widget.setLabel(str(widget.getExpr()))

def change_color_on_option(widget, t):
    """Uses widget.setColors() to change AutoColorLineEdit background color"""
    widget.logger.info(f'change background color to {t}')
    widget.setColors((widget.currentData(), 'black'))

def show_symbols(widget):
    """Uses widget.getSymbols() to print the sympy symbols in the widget's expression"""
    widget.logger.info(widget.getSymbols())

def sub_x(widget):
    """Substitutes 1.2 -> x in widget's expression, and prints solution"""
    expr = widget.getExpr()
    if expr:
        widget.logger.info(expr.evalf(subs={'x':1.2}))

def convert_to_meters(widget, t=None):
    """Convert widget value and selected units to meters, print result"""
    if t is None:
        t = widget.getUnits()
    widget.logger.info(widget.getValue() + ' <=> ' + widget.convertTo('m'))

# end helper functions
##################


# start Qt stuff
app = QApplication([])

# main window, there are other ways to make this
window = QWidget()
# put a vertical layout in the window
layout = QVBoxLayout(window)

# QLineEdit that changes color automatically (base object for the other widgets shown here)
autocolor = AutoColorLineEdit(window, text='AutoColor')
autocolor.errorCheck = lambda: check_error_typed(autocolor)

# AutoColorLineEdit, where expression is tested for safe sympy usage
sympyauto = SympyExprEdit(window, text='SympyAutoColor')
sympyauto.textChanged.connect(lambda: show_symbols(sympyauto))

# AutoColorLineEdit with a QLabel
labeledit = LabelLineEdit(window, label='result', text='3*mm + 2*inch')
labeledit.editingFinished.connect(lambda: change_label_to_result(labeledit))

# AutoColorLineEdit with a QLabel, where expression is tested for safe sympy usage
sympylabel = SympyLabelEdit(window, label='SympyLabel', text='sin(2*x)+3*pi/4.1')
sympylabel.editingFinished.connect(lambda: sub_x(sympylabel))

# AutoColorLineEdit with a QLabel, where expression is tested for safe sympy usage AS A SYMBOL
sympysymbol = SympySymbolEdit(window, label="SympySymbol")
sympysymbol.editingFinished.connect(lambda: show_symbols(sympysymbol))

# AutoColorLineEdit, QLabel, and a QComboBox
entry = EntryWidget(window, label="EntryWidget", text='pick a color',
                    options={'red':(220, 10, 10), 'blue':'blue', 'orange':rgb(255, 165, 0)}
                    )
entry.optionChanged.connect(lambda t: change_color_on_option(entry, t))

# AutoColorLineEdit, QLabel, and a QComboBox, where expression is tested for safe sympy usage
sympyentry = SympyEntryWidget(window, label='SympyEntry', options=ComboBoxOptionSets.length,
                              text='3*pi/4 * 4')
sympyentry.editingFinished.connect(lambda: convert_to_meters(sympyentry))
sympyentry.optionChanged.connect(lambda t: convert_to_meters(sympyentry))


layout.addWidget(autocolor)
layout.addWidget(sympyauto)
layout.addWidget(labeledit)
layout.addWidget(sympylabel)
layout.addWidget(sympysymbol)
layout.addWidget(entry)
layout.addWidget(sympyentry)

window.setLayout(layout)

window.show()
app.exec_()
