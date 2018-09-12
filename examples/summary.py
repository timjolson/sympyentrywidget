from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.Qt import QApplication
from PyQt5 import QtCore  # for mouse click events

from entryWidget import AutoColorLineEdit, LabelLineEdit, EntryWidget
from sympyEntryWidget import SympyAutoColorLineEdit, SympySymbolLineEdit, SympyLabelLineEdit, SympyEntryWidget

# import sys
# import logging
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)

##################
# helper functions, read their doc strings for reference
def check_error_typed(widget, *args, **kwargs):
    """Returns 'ERROR' if widget.text() == 'error', False otherwise"""
    print('check_error_typed')
    if widget.text() == 'error':
        return 'ERROR'
    return False

def show_mouse_click(widget, event, *args, **kwargs):
    """Uses widget.setText() to show if mouse click was Left or Right Click"""
    if event.button() == QtCore.Qt.LeftButton:
        widget.setText('Left Click')
    elif event.button() == QtCore.Qt.RightButton:
        widget.setText('Right Click')

def change_label_on_typing(widget, *args, **kwargs):
    """Uses widget.setLabel() to change the QLabel to widget.text()"""
    print('change label to: ' + widget.text())
    widget.setLabel(widget.text())

def change_color_on_option(widget, *args, **kwargs):
    """Uses widget.setColors() to change QLineEdit colors to (widget.getSelected(), 'black')"""
    print('change_color')
    widget.setColors((widget.getSelected(), 'black'))

def show_symbols(widget, *args, **kwargs):
    """Uses widget.getSymbols() to print the sympy symbols in the widget's expression"""
    print(widget.getSymbols())

def sub_x(widget, *args, **kwargs):
    """Substitutes 1.2 -> x in widget's expression, and prints solution"""
    expr = widget.getExpr()
    if expr:
        print(expr.evalf(subs={'x':1.2}))

def convert_from_units(widget):
    """Convert widget value and selected units to meters, print result"""
    print(
        str(widget.getExpr()*widget.getUnits()) +
          ' = ' + str(widget.convert_to('m')) +
          ' = ' + str(widget.getExpr().evalf()) + '*' + str(widget.getUnits())
    )

# end helper functions
##################


# start Qt stuff
app = QApplication([])

# main window, there are other ways to make this
window = QWidget()
# put a vertical layout in the window
layout = QVBoxLayout(window)

# QLineEdit that changes color automatically (base for the other widgets shown here)
autocolor = AutoColorLineEdit(window, startPrompt='AutoColor', isError=check_error_typed)

# AutoColorLineEdit, where expression is tested for safe sympy usage
sympyauto = SympyAutoColorLineEdit(window, startPrompt='SympyAutoColor', onEditingFinished=show_symbols)

# AutoColorLineEdit with a QLabel
labeledit = LabelLineEdit(window, label='Click Here', startPrompt='LabelLineEdit', onLabelClick=show_mouse_click)

# AutoColorLineEdit with a QLabel, where expression is tested for safe sympy usage
sympylabel = SympyLabelLineEdit(window, label='SympyLabel', startPrompt='sin(2*x)+3*pi/4.1', onLabelClick=sub_x)

# AutoColorLineEdit with a QLabel, where expression is tested for safe sympy usage AS A SYMBOL
sympysymbol = SympySymbolLineEdit(window, label="SympySymbol", onEditingFinished=show_symbols)

# AutoColorLineEdit, QLabel, and a QComboBox
entry = EntryWidget(window, label="EntryWidget", startPrompt='pick a color',
                    options=['red', 'blue', 'orange'], onOptionChanged=change_color_on_option)

# AutoColorLineEdit, QLabel, and a QComboBox, where expression is tested for safe sympy usage
sympyentry = SympyEntryWidget(window, label='SympyEntry', options=['mm', 'm', 'inch', 'km', 'ft'],
                              startPrompt='3*pi/4 * 4', onEditingFinished=convert_from_units,
                              onOptionChanged=convert_from_units)


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
