from qt_utils.designer import WidgetPluginFactory

from sympyentrywidget import \
    SympyExprEdit, SympyEntryWidget, SympySymbolEdit

SympyAutoColorLineEditPlugin = WidgetPluginFactory(SympyExprEdit,
                                                   toolTip='QLineEdit with Sympy error checking and automatic colors')
SympySymbolLineEditPlugin = WidgetPluginFactory(SympySymbolEdit,
                                                toolTip='SympyLabelEdit for creating sympy.Symbol')
SympyEntryWidgetPlugin = WidgetPluginFactory(SympyEntryWidget,
                                             toolTip='SympyLabelEdit and QComboBox for unit conversions')
