from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.Qt import QApplication
from entrywidget import AutoColorLineEdit, EntryWidget


# <editor-fold desc="helper functions, read their doc strings for reference">
def check_error_typed(widget):
    """Returns 'ERROR' if widget.text() == 'error', False otherwise"""
    print('check_error_typed: ', widget.text())
    if widget.text() == 'error':
        return 'ERROR'
    return False

def check_text_matches_option(widget):
    """Compares widget.text() and widget.getSelected(), returns if they are =="""
    v = widget.text() == widget.getSelected()
    print('check_text_matches_option:', v)
    return v

def printer(label):
    """Creates a print function that prefixes the output with `label`"""
    return lambda *args: print(label, *args)
# </editor-fold>


# start Qt stuff
app = QApplication([])
# main window, there are other ways to make this
window = QWidget()

# QLineEdit that changes color automatically
autocolor = AutoColorLineEdit(window, text='AutoColorLineEdit', errorCheck=check_error_typed)
autocolor.hasError[object].connect(printer('hasError[object] !!!'))
# autocolor.hasError[str].connect(printer('hasError[str] !!!'))
# autocolor.hasError.connect(printer('hasError !!!'))
autocolor.errorCleared.connect(lambda: print(':) NO MORE ERROR :)'))

# AutoColorLineEdit and a DictComboBox
entry = EntryWidget(window, text='EntryWidget',
                    options={'a':'data A', 'b':'data B', 'c':'data C'},
                    errorCheck=check_text_matches_option)
entry.optionChanged[str].connect(printer('optionChanged[str]'))
# entry.optionChanged.connect(printer('optionChanged'))
# entry.optionIndexChanged[int].connect(printer('optionIndexChanged[int]'))
# entry.optionIndexChanged.connect(printer('optionIndexChanged'))
entry.dataChanged[object].connect(printer('dataChanged[object]'))
# entry.dataChanged[str].connect(printer('dataChanged[str]'))
# entry.dataChanged.connect(printer('dataChanged'))


# put a vertical layout in the window
layout = QVBoxLayout(window)

# add widgets to layout
layout.addWidget(autocolor)
layout.addWidget(entry)

# show things
window.show()
app.exec_()
