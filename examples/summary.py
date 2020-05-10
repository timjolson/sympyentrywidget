from PyQt5.QtWidgets import QWidget, QVBoxLayout
from entrywidget import AutoColorLineEdit, EntryWidget

# Qt stuff
# from PyQt5.Qt import QApplication  # optional, can be started from widget.mkQApp()
# from PyQt5.QtWidgets import QApplication
# app = QApplication(sys.argv)

# start Qt
app = EntryWidget.mkQApp()

# <editor-fold desc="Support Funcs">
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


# main window, there are other ways to make this
window = QWidget()

# QLineEdit that changes color automatically
autocolor = AutoColorLineEdit(window, text='AutoColorLineEdit', errorCheck=check_error_typed)
autocolor.hasError[object].connect(printer('hasError[object] !!!'))
# autocolor.hasError[str].connect(printer('hasError[str] !!!'))
# autocolor.hasError.connect(printer('hasError !!!'))
autocolor.errorCleared.connect(lambda: print(':) NO MORE ERROR :)'))
autocolor.setToolTip(
    """
    Typing 'error' causes:
        box to have error (errorCheck)
        log the error (hasError)
    Clear 'error' causes:
        error status cleared (errorCheck)
        log the error (errorCleared)
    """
)

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
entry.setToolTip(
    """
    Change combobox cuases:
        log new option (optionChanged)
        log data assigned to new option (dataChanged)
    Text matches combobox causes:
        box to have error (errorCheck)
        log the error (hasError)
    """
)

# put a vertical layout in the window
layout = QVBoxLayout(window)

# add widgets to layout
layout.addWidget(autocolor)
layout.addWidget(entry)

# show things
window.show()
app.exec_()
