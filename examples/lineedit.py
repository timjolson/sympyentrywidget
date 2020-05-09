from entrywidget import AutoColorLineEdit
from PyQt5.Qt import QApplication
from PyQt5 import QtWidgets
import sys
import logging

# log to console
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# start Qt
app = QApplication(sys.argv)

# <editor-fold desc="Support Funcs">
def detect_error(w):
    print("Checking for 'error'")
    return w.text() == 'error'

def announce_error(w):
    print(w.name + ': There IS an Error')

def announce_no_error(w):
    print(w.name + ': There is NO Error')

def print_entered_text(w):
    print(w.name + ": Entered Text is '"+ w.text() + "'")

def do_whats_typed(w):
    if w.text() == 'auto':
        print(w.name + ": Changing to Automatic colors")
        w.setColors()
    if w.text() == 'manual':
        print(w.name + ": Changing to Manual colors")
        w.setColors(('black', 'white'))
    if w.text() == 'readonly':
        w.setReadOnly(True)
        print(w.name + ': Entry is ReadOnly')
    if w.text() == 'disable':
        w.setDisabled(True)
        print(w.name + ': Entry is Disabled')
    if w.text() == 'close':
        print(w.name + ': Closing Window')
        w.window().close()
# </editor-fold>

widgetDefault = AutoColorLineEdit(text="Basic Widget")
widgetDefault.setWindowTitle("Basic Widget")
widgetDefault.show()
app.exec_()

widgetDefault = AutoColorLineEdit(errorCheck=detect_error, text="Type 'error'")
widgetDefault.hasError.connect(lambda: announce_error(widgetDefault))
widgetDefault.setWindowTitle("errorCheck")
widgetDefault.show()
app.exec_()

widgetDefault = AutoColorLineEdit(liveErrorChecking=False, errorCheck=detect_error)
widgetDefault.setText("Type 'error', press ENTER")
widgetDefault.setWindowTitle("liveErrorChecking=False")
widgetDefault.hasError.connect(lambda: announce_error(widgetDefault))
widgetDefault.errorCleared.connect(lambda: announce_no_error(widgetDefault))
widgetDefault.setMinimumWidth(250)
widgetDefault.show()
app.exec_()


widget0 = AutoColorLineEdit(
    objectName='widget0',  # object name inside Qt, also can be used for logging
    text='startPrompt',  # box's text on startup
    liveErrorChecking=True,  # whether to run isError() every text change, or only when editing is finished
    readOnly=False,  # whether the text box is readOnly or not
    errorCheck=detect_error
)
widget0.hasError.connect(lambda: announce_error(widget0))
widget0.textChanged.connect(lambda: print_entered_text(widget0))
widget0.editingFinished.connect(lambda: do_whats_typed(widget0))
widget0.setToolTip(
"""
Typing anything causes:
    error checking (liveErrorChecking=True)
    log the new text (textChanged)

Typing 'error' causes:
    box to have error (errorCheck)
    log the error (hasError)

Try typing the following strings and pressing RETURN/ENTER: (editingFinished)
    'auto' to change the box to automatic colors.
    'manual' to change the box to manual colors.
    'readonly' to make the box readonly.
    'disable' to disable the box.
    'close' to close the window.
"""
)


widget1 = AutoColorLineEdit(objectName='widget1', errorCheck=detect_error)
widget1.hasError.connect(lambda: announce_error(widget1))
widget1.editingFinished.connect(lambda: print_entered_text(widget1))
widget1.setToolTip(
"""
Typing anything causes:
    error checking (liveErrorChecking=True)

Typing 'error' causes:
    box to have error (errorCheck)
    log the error (hasError)

Hit ENTER / finish editing causes:
    print the entered text (editingFinished)
"""
)

widget2 = AutoColorLineEdit(
    objectName='widget 2',
    text='error',
    liveErrorChecking=False,
    errorCheck=detect_error
)
widget2.hasError.connect(lambda: announce_error(widget2))
widget2.errorCleared.connect(lambda: announce_no_error(widget2))
widget2.editingFinished.connect(lambda: do_whats_typed(widget2))
widget2.setToolTip(
    """
Typing DOES NOT cause error checking (liveErrorChecking=False)

Typing then pressing RETURN/ENTER causes:
    errorCheck (liveErrorChecking=False)
    log the error (hasError)
    log lack of error (errorCleared)

Try typing the following strings and pressing RETURN/ENTER: (editingFinished)
    'auto' to change the box to automatic colors.
    'manual' to change the box to manual colors.
    'readonly' to make the box readonly.
    'disable' to disable the box.
    'close' to close the window.
"""
)

print("\n-----------------------")
widget3 = AutoColorLineEdit(
    text="custom colors",
    liveErrorChecking=False,
)
widget3.setObjectName('widget 3')
widget3.textChanged.connect(lambda: do_whats_typed(widget3))
widget3.setColors(('black', 'white'))
widget3.setToolTip(
    """
Typing DOES NOT cause error checking (liveErrorChecking=False)

Try typing the following strings: (textChanged)
    'auto' to change the box to automatic colors.
    'manual' to change the box to manual colors.
    'readonly' to make the box readonly.
    'disable' to disable the box.
    'close' to close the window.
"""
)

print("\n-----------------------")
window = QtWidgets.QWidget()
window.setObjectName('main window')
layout = QtWidgets.QVBoxLayout(window)
layout.addWidget(widgetDefault)
layout.addWidget(widget0)
layout.addWidget(widget1)
layout.addWidget(widget2)
layout.addWidget(widget3)

info = QtWidgets.QTextEdit(
    """Hover over widgets for help.
    Watch console for logging.
    """, window)
layout.addWidget(info)

window.setLayout(layout)
window.show()
app.exec_()
