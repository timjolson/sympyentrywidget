from qt_utils.designer import WidgetPluginFactory

from sympyEntryWidget import \
    SympyAutoColorLineEdit, SympyEntryWidget, SympyLabelLineEdit, SympySymbolLineEdit

SympyAutoColorLineEditPlugin = WidgetPluginFactory(SympyAutoColorLineEdit,
                                                   toolTip='QLineEdit with Sympy error checking and automatic colors')
SympyLabelLineEditPlugin = WidgetPluginFactory(SympyLabelLineEdit,
                                               toolTip='QLabel and SympyAutoColorLineEdit')
SympySymbolLineEditPlugin = WidgetPluginFactory(SympySymbolLineEdit,
                                                toolTip='SympyLabelLineEdit for creating sympy.Symbol')
SympyEntryWidgetPlugin = WidgetPluginFactory(SympyEntryWidget,
                                             toolTip='SympyLabelLineEdit and QComboBox for unit conversions')
