import pytest
import sys

# test helpers
from qt_utils.helpers_for_tests import (show, change_color_on_option, check_error_typed, set_title_on_error)

# dicts/tuples/lists for color testing (from __init__.py)
from . import *
# helpers
from qt_utils import getCurrentColor

# class to test
from entrywidget import EntryWidget

# Qt stuff
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

# logging stuff
import logging

# logging.basicConfig(stream=sys.stdout, filename='/logs/EntryWidget.log', level=logging.INFO)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG-1)
app = QApplication(sys.argv)


def check_text_matches_option(widget):
    """Compares widget.text() and widget.getSelected(), returns if they are =="""
    return widget.text() == widget.getSelected()


def test_constructor_basic(qtbot):
    widget = EntryWidget()
    show(locals())


def test_constructor_readOnly(qtbot):
    widget = EntryWidget(readOnly=True)
    show(locals())
    assert widget.lineEdit.isReadOnly() is True
    assert widget.isReadOnly() is True
    assert widget.comboBox.isEnabled() is False
    assert widget.optionFixed() is True

    widget = EntryWidget(readOnly=False)
    show(locals())
    assert widget.lineEdit.isReadOnly() is False
    assert widget.isReadOnly() is False
    assert widget.comboBox.isEnabled() is True
    assert widget.optionFixed() is False


def test_constructor_options(qtbot):
    widget = EntryWidget(options=test_options_good)
    show(locals())
    assert widget.getOptions() == {k:k for k in test_options_good}
    assert widget.getSelected() == test_options_good[0]


def test_constructor_optionFixed(qtbot):
    widget = EntryWidget(optionFixed=True)
    show(locals())
    assert widget.comboBox.isEnabled() is False
    assert widget.optionFixed() is True

    widget = EntryWidget(optionFixed=False)
    show(locals())
    assert widget.comboBox.isEnabled() is True
    assert widget.optionFixed() is False


def test_embed_widgets(qtbot):
    from PyQt5.QtWidgets import QVBoxLayout, QWidget
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.addWidget(EntryWidget())
    layout.addWidget(EntryWidget())
    window.setLayout(layout)
    show({'qtbot':qtbot, 'widget':window})


def test_setReadOnly(qtbot):
    widget = EntryWidget()
    show(locals())
    widget.setReadOnly(True)
    assert widget.lineEdit.isReadOnly() is True
    assert widget.isReadOnly() is True
    assert widget.comboBox.isEnabled() is False
    assert widget.optionFixed() is True

    widget.setReadOnly(False)
    assert widget.lineEdit.isReadOnly() is False
    assert widget.isReadOnly() is False
    assert widget.comboBox.isEnabled() is True
    assert widget.optionFixed() is False


def test_setEnabled(qtbot):
    widget = EntryWidget()
    show(locals())
    widget.setEnabled(False)
    assert widget.lineEdit.isEnabled() is False
    assert widget.isReadOnly() is False
    assert widget.comboBox.isEnabled() is False
    assert widget.optionFixed() is True

    widget.setEnabled(True)
    assert widget.lineEdit.isEnabled() is True
    assert widget.isReadOnly() is False
    assert widget.comboBox.isEnabled() is True
    assert widget.optionFixed() is False


def test_setOptions(qtbot):
    widget = EntryWidget()
    show(locals())
    widget.setOptions(test_options_good)
    assert widget.getOptions() == {k:k for k in test_options_good}
    assert widget.getSelected() == test_options_good[0]


def test_setFixedOption(qtbot):
    widget = EntryWidget()
    show(locals())
    widget.setOptionFixed(True)
    assert widget.comboBox.isEnabled() is False
    assert widget.optionFixed() is True

    widget = EntryWidget()
    show(locals())
    widget.setOptionFixed(False)
    assert widget.comboBox.isEnabled() is True
    assert widget.optionFixed() is False


def test_onOptionChanged(qtbot):
    widget = EntryWidget(options=test_options_colors)
    show(locals())
    widget.optionChanged.connect(lambda: change_color_on_option(widget))

    widget.setSelected(test_options_colors[1])
    assert getCurrentColor(widget.lineEdit, 'Window')[0][0] == test_options_colors[1]

    widget.setSelected(test_options_colors[0])
    assert getCurrentColor(widget.lineEdit, 'Window')[0][0] == test_options_colors[0]

    widget.setSelected(test_options_colors[2])
    assert getCurrentColor(widget.lineEdit, 'Window')[0][0] == test_options_colors[2]


def test_setError(qtbot):
    widget = EntryWidget()
    show(locals())
    widget.setError(True)
    assert widget.getError() is True
    assert getCurrentColor(widget.lineEdit, 'Window').names[0] == widget.defaultColors['error'][0]
    widget.setError(False)
    assert widget.getError() is False
    assert getCurrentColor(widget.lineEdit, 'Window').names[0] == widget.defaultColors['blank'][0]


def test_errorCheck_live(qtbot):
    widget = EntryWidget(errorCheck=check_error_typed)
    show(locals())
    logging.debug('typing...')
    qtbot.keyClicks(widget.lineEdit, 'erro')
    assert widget.getError() is False
    qtbot.keyClicks(widget.lineEdit, 'r')
    logging.debug('finished typing...')
    assert widget.getError() == 'ERROR'
    assert getCurrentColor(widget.lineEdit, 'Window').names[0] == widget.defaultColors['error'][0]
    qtbot.keyPress(widget.lineEdit, QtCore.Qt.Key_Backspace)
    assert widget.getError() is False
    assert getCurrentColor(widget.lineEdit, 'Window').names[0] == widget.defaultColors['default'][0]


def test_errorCheck(qtbot):
    widget = EntryWidget(liveErrorChecking=False, errorCheck=check_error_typed)
    show(locals())
    assert widget.getError() is False
    logging.debug('typing...')
    qtbot.keyClicks(widget.lineEdit, 'erro')
    assert widget.getError() is False
    qtbot.keyClicks(widget.lineEdit, 'r')
    logging.debug('finished typing...')
    assert widget.getError() is False
    qtbot.keyPress(widget.lineEdit, QtCore.Qt.Key_Return)
    assert widget.getError() == 'ERROR'
    assert getCurrentColor(widget.lineEdit, 'Window').names[0] == widget.defaultColors['error'][0]
    qtbot.keyPress(widget.lineEdit, QtCore.Qt.Key_Backspace)
    assert widget.getError() == 'ERROR'
    qtbot.keyPress(widget.lineEdit, QtCore.Qt.Key_Return)
    assert widget.getError() is False
    assert getCurrentColor(widget.lineEdit, 'Window').names[0] == widget.defaultColors['default'][0]


def test_errorCheck_with_combobox(qtbot):
    widget = EntryWidget(errorCheck=check_text_matches_option, options=['a', 'b'])
    show(locals())
    qtbot.keyClicks(widget.lineEdit, 'b')
    assert widget.getError() is False
    qtbot.keyPress(widget.lineEdit, QtCore.Qt.Key_Backspace)
    qtbot.keyPress(widget.lineEdit, 'a')
    assert widget.getError() is True
    assert getCurrentColor(widget.lineEdit, 'Window').names[0] == widget.defaultColors['error'][0]
    widget.setSelected('b')
    assert widget.getError() is False
    qtbot.keyPress(widget.lineEdit, QtCore.Qt.Key_Backspace)
    qtbot.keyPress(widget.lineEdit, 'b')
    assert widget.getError() is True
    assert getCurrentColor(widget.lineEdit, 'Window').names[0] == widget.defaultColors['error'][0]


def test_hasError(qtbot):
    widget = EntryWidget()
    widget.hasError.connect(lambda: set_title_on_error(widget))
    show(locals())

    assert widget.getError() is False
    widget.setError(False)
    assert widget.getError() is False
    widget.setError(True)
    assert widget.windowTitle() == 'ERROR'
    widget.clearError()
    assert widget.getError() is None
