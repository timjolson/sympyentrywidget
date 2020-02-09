from qt_utils.designer import WidgetPluginFactory

from sympyentrywidget import \
    ExprEdit, SympyEntryWidget, SymbolEdit, UnitEdit, DimensionEdit

SympyExprEditPlugin = WidgetPluginFactory(ExprEdit,
                                          toolTip='QLineEdit with Sympy error checking and automatic colors')
SympyUnitEditPlugin = WidgetPluginFactory(UnitEdit,
                                          toolTip='QLineEdit with Sympy unit support')
SympyDimensionEditPlugin = WidgetPluginFactory(DimensionEdit,
                                               toolTip='QLineEdit with Sympy unit support and enforced output dimensions')
SympySymbolEditPlugin = WidgetPluginFactory(SymbolEdit,
                                            toolTip='SympyLabelEdit for creating sympy.Symbol')
SympyEntryWidgetPlugin = WidgetPluginFactory(SympyEntryWidget,
                                             toolTip='SympyLabelEdit and QComboBox for unit conversions')
