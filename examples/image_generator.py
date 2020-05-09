from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.Qt import QApplication
from entrywidget import AutoColorLineEdit, EntryWidget

app = QApplication([])

window = QWidget()
window.setWindowTitle('EntryWidget examples')
layout = QVBoxLayout(window)

autocolor = AutoColorLineEdit(window, text='AutoColorLineEdit')
layout.addWidget(autocolor)

layout.addWidget(AutoColorLineEdit(text=''))

errorwidget = AutoColorLineEdit(text='error', errorCheck=lambda w: (w.text() == 'error'))
layout.addWidget(errorwidget)

entry = EntryWidget(window, text='EntryWidget', options=['QComboBox'])
layout.addWidget(entry)

window.setLayout(layout)
window.show()
app.exec_()
