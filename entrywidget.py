from PyQt5.QtWidgets import QLineEdit, QWidget, QHBoxLayout
from PyQt5.QtCore import pyqtProperty, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtGui import QColor
from PyQt5.Qt import QApplication
from qt_utils import loggableQtName, ErrorMixin
from qt_utils.widgets import DictComboBox
from delegated import delegated
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def mkQApp(*args):
    qa = QApplication.instance()
    if qa is None:
        qa = QApplication(list(args))
    return qa


def _isColorTuple(colors):
    """See if 'colors' matches the format for a colors tuple.

    :param colors: tuple to check format of
    :return: bool
        False if colors == None
        True if colors == correct format
    """
    if colors is None:
        return False

    if not isinstance(colors, (tuple, list)): return False
    if not len(colors) == 2: return False
    if not all(isinstance(c, (str, tuple, QColor)) for c in colors): return False
    return True


def _isColorDict(colors):
    """See if 'colors' matches the format for a colors dict.

    :param colors: dict to check format of
    :return: bool
        False if colors == None
        True if colors == correct format
    """
    if colors is None:
        return False

    # check format
    if not isinstance(colors, dict): return False
    if not all(_isColorTuple(c) for c in colors.values()): return False
    return True


class AutoColorLineEdit(QLineEdit, ErrorMixin):
    """A QLineEdit with error checking options and automatic color updates.
        Useful signals:
            hasError([]],[object],[str])  # emitted when bool(error status) is True
            errorChanged([],[object],[str])  # emitted when error status changes
            errorCleared  # emitted when bool(error status) is changed to False
            editingFinished  # emitted when Enter/Return pressed or focus is changed out of QLineEdit
            textChanged(str)  # emitted when text changes at all

        All arguments are optional and must be provided by keyword, except 'parent' which can be positional.
        :param parent: Parent Qt Object (default None for individual widget)
        :param errorCheck: callable, returns error status, called with widget as first argument
        :param objectName: str, name of object for logging and within Qt
        :param text: str, starting text
        :param colors: dict or tuple of colors; see help(setColors) for formatting
        :param readOnly: bool, whether the text box is editable
        :param liveErrorChecking: bool, whether error checking occurs
                    after every keystroke (=True) or only after text editing is finished (=False)
        """
    name = loggableQtName

    defaultColors = {
        'error-readonly': ('orangered', 'white'),
        'error': ('yellow', 'black'),
        'default': ('white', 'black'),
        'blank': ('lightblue', 'black'),
        'disabled': ('#F0F0F0', 'black'),
        'readonly': ('#F0F0F0', 'black')
    }

    defaultArgs = {
        'colors': None,
        'liveErrorChecking': True,
        'errorCheck': None,
        'text': ''
    }

    def __init__(self, parent=None, **kwargs):
        self._autoColors = self.defaultColors.copy()
        self._liveErrorChecking = kwargs.pop('liveErrorChecking', self.defaultArgs['liveErrorChecking'])

        colors = kwargs.pop('colors', self.defaultArgs['colors'])
        ec = kwargs.pop('errorCheck', self.defaultArgs['errorCheck'])

        QLineEdit.__init__(self, parent=parent, **kwargs)
        ErrorMixin.__init__(self)

        self.logger = logging.getLogger(self.name)
        self.logger.addHandler(logging.NullHandler())

        # connect signals to do error checking, color updating
        self.textChanged[str].connect(self._onTextChanged)
        self.editingFinished.connect(self._onEditingFinished)
        self.errorChanged[object].connect(lambda o: self.update())

        if colors:
            self.setColors(colors)
        else:
            super().setStyleSheet(self.makeStyleString())

        if ec is not None:
            self.errorCheck = lambda s: ec(self)

        try:
            self.setError(self.errorCheck(self))
        except:
            pass

    def _onEditingFinished(self):
        self.logger.log(logging.DEBUG-1, 'editingFinished()')
        self.setError(self.errorCheck(self))

    def _onTextChanged(self, text):
        self.logger.log(logging.DEBUG-1, f"textChanged('{text}')")

        if self._liveErrorChecking is True:
            err = self.errorCheck(self)
            if err != self.getError():
                self.setError(err)
                return
        self.update()

    def getStatus(self):
        """Get widget status for color selection.

        :return: str, key for use in colors dict
        """
        if bool(self._error):
            status = 'error'
            if self.isEnabled() is False or self.isReadOnly() is True:
                status += '-readonly'
        elif self.isEnabled() is False:
            status = 'disabled'
        elif self.isReadOnly() is True:
            status = 'readonly'
        elif self.text() == '':
            status = 'blank'
        else:
            status = 'default'
        return status
    status = pyqtProperty(str, getStatus)

    def makeStyleString(self, colors=None):
        """Get a styleSheet string built from provided 'colors' or the defaults.

        :param colors: None-> use default colors
            OR str-> key for colors dict
            OR colors dict->update stored colors->use provided colors
            OR colors tuple->use provided colors
        :return: str, use in setStyleSheet()
        """
        if colors is None:
            colors = self._autoColors
        elif isinstance(colors, str):
            colors = self._autoColors[colors]

        if _isColorDict(colors):
            string = ''
            for k, v in colors.items():
                v0, v1 = v
                if isinstance(v0, QColor):
                    v0 = v0.getRgb()[:2]
                if isinstance(v1, QColor):
                    v1 = v1.getRgb()[:2]

                if isinstance(v0, tuple):
                    v0 = "rgb{}".format(str(v0[:])).replace(' ', '')
                if isinstance(v1, tuple):
                    v1 = "rgb{}".format(str(v1[:])).replace(' ', '')
                string += "AutoColorLineEdit[status='" + str(k) + "'] {background-color: " + str(v0) + "; color: " + str(v1) + ";}\n"

        elif _isColorTuple(colors):
            v0, v1 = colors[0], colors[1]
            if isinstance(v0, QColor):
                v0 = v0.getRgb()[:2]
            if isinstance(v1, QColor):
                v1 = v1.getRgb()[:2]

            if isinstance(v0, tuple):
                v0 = "rgb{}".format(str(v0[:])).replace(' ', '')
            if isinstance(v1, tuple):
                v1 = "rgb{}".format(str(v1[:])).replace(' ', '')
            string = "AutoColorLineEdit {background-color: " + str(v0) + "; color: " + str(v1) + ";}\n"

        else:
            raise TypeError(f'Invalid format: {type(colors)} {colors}')
        return string

    def setLiveErrorChecking(self, mode):
        """Enable or disable liveErrorChecking.

        :param mode: bool
        :return:
        """
        self._liveErrorChecking = mode

        if mode is True:
            self.setError(self.errorCheck(self))

    def update(self):
        """Update widget colors"""
        # self.logger.log(logging.DEBUG - 1, "update: status: '%s' error: '%s' disabled: %s readonly: %s text: '%s'"%
        #             (self.status, str(self.getError()), str(not self.isEnabled()), str(self.isReadOnly()), self.text())
        #             )
        self.style().polish(self)

    def autoColors(self):
        """Get current color settings dict.
        :return: dict
        """
        return self._autoColors

    def setColors(self, colors=None):
        """Set the widget's colors.
        If colors is `None`, uses stored automatic colors.
        If colors is tuple-like, assigns static colors.

        If colors is a dict (format below), updates the automatic colors,
            where each key represents a different `widget.status`.
        A custom set of `status`s can be used by overriding `getStatus` and providing a custom dict.

        :param colors: dict of tuples of color strings or QColors
            dict format:
                *colors={
                    'default': X,           # normal editing mode
                    'blank': X,             # box is editable but blank
                    'disabled': X,          # box is not editable or selectable
                    'readonly': X,          # box is not editable
                    'error': X,             # box is editable and has an error
                    'error-readonly': X     # box is not editable, but has an error
                }
                *all keys are optional, dict updates currently stored autoColors.
                Where each X matches the format below.

            tuple format (backgroundColor, textColor):
                e.g. ('black', QColor)  //  ('#FFFFFF', 'white')  //  (QColor, '#FFFFFF')
        :return:
        """
        # update _autoColors with provided colors
        if _isColorDict(colors):
            self._autoColors.update(colors)
            colors = self._autoColors
        elif colors is None:
            colors = self._autoColors
        elif _isColorTuple(colors):
            pass
        elif isinstance(colors, str):
            colors = self._autoColors[colors]
        else:
            raise TypeError(f"Provide `None`, color dict, color tuple, or str; not {colors}")
        super().setStyleSheet(self.makeStyleString(colors))

    def setReadOnly(self, status):
        """Set the box editable or fixed.

        :param status: box's editable status
        :return:
        """
        super().setReadOnly(status)
        self.setClearButtonEnabled(not status)
        self.update()

    def setDisabled(self, status=True):
        """Set the box disabled or enabled.

        :param status: NOT box's enabled status
            True: unselectable, uneditable
            False: selectable (editability dictated by readOnly)
        :return:
        """
        self.setEnabled(not status)

    def setEnabled(self, status=True):
        """Set the box disabled or enabled.

        :param status: box's enabled status
            True: selectable (editability dictated by readOnly)
            False: unselectable, uneditable
        :return:
        """
        super().setEnabled(status)
        self.setClearButtonEnabled(status)
        self.update()

    @classmethod
    def popArgs(cls, kwargs):
        '''Remove(pop) widget's defaultArgs from kwargs, and return
        defaultArgs having been updated by the pop'ed kwargs.

        :param kwargs: dict
        :return: dict
        '''
        args = cls.defaultArgs.copy()
        for k in args:
            if k in kwargs:
                args[k] = kwargs.pop(k)
        return args

    mkQApp = mkQApp


class EntryWidget(QWidget):
    """A DictComboBox after an AutoColorLineEdit.
    DictComboBox (.comboBox):
        Set options with obj.setOptions(['opt1', 'opt2', 'op3'])
        Get options with obj.getOptions()
        Set selected with obj.setSelected('opt2')
        Get selected with obj.getSelected()
        Set/unset ReadOnly with obj.setOptionFixed(bool)

    Additional signals (on top of AutoColorLineEdit signals):
        optionChanged([], [str])  # emits newly selected option when selection is changed
        optionIndexChanged([], [int])  # emits new selection index when changed
        dataChanged([], [object])  # emits data attached to new selection

    All arguments are optional and must be provided by keyword, except 'parent' which can be positional.
    kwargs listed here will be passed to constructors of AutoColorLineEdit/DictComboBox

    Widget kwargs
    :param parent: Parent Qt Object (default None for individual widget)
    :param errorCheck: callable, returns error status, called with widget as first argument
    :param objectName: str, name of object for logging and within Qt
    :param readOnly: bool, whether the text box is editable

    QLineEdit kwargs
    :param text: str, starting text
    :param colors: dict or tuple of colors; see help(setColors) for formatting
    :param liveErrorChecking: bool, whether error checking occurs
                after every keystroke (=True) or only after text editing is finished (=False)

    DictComboBox kwargs
    :param options: [str, str, ...] or {str:data, str:data, ...}
    :param optionFixed: bool, whether option is fixed or can be changed
    """
    name = loggableQtName
    errorChanged = ErrorMixin.errorChanged
    errorCleared = ErrorMixin.errorCleared
    hasError = ErrorMixin.hasError

    defaultColors = AutoColorLineEdit.defaultColors.copy()
    defaultArgs = AutoColorLineEdit.defaultArgs.copy()
    defaultArgs.update({'options': {'opt1':'opt1 Data', 'opt2':'opt2 Data'}, 'optionFixed': False})

    # delegate methods to DictComboBox
    getSelected, setSelected, setOptionFixed, currentData = \
        delegated.methods('comboBox', 'currentText, setCurrentText, setDisabled, currentData')
    getOptions, setOptions = delegated.methods('comboBox', 'allItems setAllItems')

    # delegate methods to AutoColorLineEdit
    text, setText = delegated.methods('lineEdit', 'text, setText')
    text_ = pyqtProperty(str, lambda s: s.lineEdit.text(), lambda s, t: s.lineEdit.setText(t))
    clear, setClearButtonEnabled = delegated.methods('lineEdit', 'clear setClearButtonEnabled')
    setColors, setLiveErrorChecking = delegated.methods('lineEdit', 'setColors, setLiveErrorChecking')
    setError, getError, clearError = delegated.methods('lineEdit', 'setError, getError, clearError')

    # delegate AutoColorLineEdit signals
    textChanged, editingFinished, textEdited = delegated.attributes('lineEdit', 'textChanged, editingFinished, textEdited')

    # delegate DictComboBox signals
    dataChanged = delegated.attribute('comboBox', 'dataChanged')
    # signals triggered by DictComboBox (re-emitted to allow multiple formats)
    optionChanged = pyqtSignal([],[str])  # currentTextChanged
    optionIndexChanged = pyqtSignal([],[int])  # currentIndexChanged

    def __init__(self, parent=None, **kwargs):
        QWidget.__init__(self, parent=parent)
        readOnly = kwargs.pop('readOnly', False)
        self.setupUi(kwargs)
        if readOnly:
            self.setReadOnly(readOnly)

        try:
            self.setError(self.errorCheck(self))
        except:
            pass

    def setupUi(self, kwargs):
        options = kwargs.pop('options', self.defaultArgs['options'])
        optionFixed = kwargs.pop('optionFixed', self.defaultArgs['optionFixed'])

        # connect signals to simpler versions
        self.errorChanged[object].connect(lambda o: self.errorChanged[str].emit(str(o)))
        self.errorChanged[object].connect(lambda o: self.errorChanged.emit())
        self.hasError[object].connect(lambda o: self.hasError[str].emit(str(o)))
        self.hasError[object].connect(lambda o: self.hasError.emit())
        self.optionChanged[str].connect(lambda o: self.optionChanged.emit())
        self.optionIndexChanged[int].connect(lambda o: self.optionIndexChanged.emit())

        self.logger = logging.getLogger(self.name)
        self.logger.addHandler(logging.NullHandler())

        ec = kwargs.get('errorCheck', None)
        if ec is not None:
            kwargs['errorCheck'] = lambda s: ec(self)
        self.lineEdit = lineEdit = AutoColorLineEdit(parent=self, **kwargs)
        lineEdit.errorCleared.connect(self.errorCleared.emit)
        lineEdit.errorChanged[object].connect(self.errorChanged[object].emit)
        lineEdit.hasError[object].connect(self.hasError[object].emit)

        self.comboBox = combo = DictComboBox(parent=self, options=options)
        combo.setDisabled(optionFixed)
        # combo.setSizeAdjustPolicy(DictComboBox.AdjustToContents)
        combo.currentIndexChanged[int].connect(self.optionIndexChanged[int].emit)
        combo.currentTextChanged[str].connect(self.optionChanged[str].emit)
        combo.currentTextChanged[str].connect(self._onOptionChanged)

        layout = QHBoxLayout(self)
        layout.addWidget(lineEdit)
        layout.addWidget(combo)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    @staticmethod
    def errorCheck(self):
        return self.lineEdit.errorCheck(self)

    def _onOptionChanged(self, text):
        self.logger.log(logging.DEBUG-1, f"optionChanged('{text}')")
        self.setError(self.errorCheck(self))

    def optionFixed(self):
        return not self.comboBox.isEnabled()

    def setEnabled(self, status):
        """Set the box disabled or enabled.

        :param status: box's enabled status
            True: selectable (editability dictated by readOnly)
            False: unselectable, uneditable
        :return:
        """
        self.comboBox.setEnabled(status)
        self.lineEdit.setEnabled(status)

    def setReadOnly(self, status):
        """Set the box editable or fixed.

        :param status: box's editable status
            True: uneditable
            False: editable
        :return:
        """
        self.comboBox.setEnabled(not status)
        self.lineEdit.setReadOnly(status)

    def isReadOnly(self):
        return self.lineEdit.isReadOnly() and (not self.comboBox.isEnabled())

    mkQApp = mkQApp

__all__ = ['AutoColorLineEdit', 'EntryWidget']
