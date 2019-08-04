from qt_utils.designer import WidgetPluginFactory

from sympyentrywidget import \
    SympyExprEdit, SympyEntryWidget, SympySymbolEdit, SympyUnitEdit

SympyExprEditPlugin = WidgetPluginFactory(SympyExprEdit,
                                                   toolTip='QLineEdit with Sympy error checking and automatic colors')
SympyUnitEditPlugin = WidgetPluginFactory(SympyUnitEdit,
                                                   toolTip='QLineEdit with Sympy unit support')
SympySymbolEditPlugin = WidgetPluginFactory(SympySymbolEdit,
                                                toolTip='SympyLabelEdit for creating sympy.Symbol')
SympyEntryWidgetPlugin = WidgetPluginFactory(SympyEntryWidget,
                                             toolTip='SympyLabelEdit and QComboBox for unit conversions')
