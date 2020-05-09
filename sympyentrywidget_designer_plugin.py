from qt_utils.designer import WidgetPluginFactory

from sympyentrywidget import \
    AutoColorLineEdit, EntryWidget, ExprEdit, SympyEntryWidget, SymbolEdit, UnitEdit, DimensionEdit

AutoColorLineEditPlugin = WidgetPluginFactory(AutoColorLineEdit,
                                              toolTip='QLineEdit with automatic colors')
EntryWidgetPlugin = WidgetPluginFactory(EntryWidget,
                                        toolTip='AutoColorLineEdit and DictComboBox')
ExprEditPlugin = WidgetPluginFactory(ExprEdit,
                                          toolTip='QLineEdit with Sympy error checking and automatic colors')
UnitEditPlugin = WidgetPluginFactory(UnitEdit,
                                          toolTip='QLineEdit with Sympy unit support')
DimensionEditPlugin = WidgetPluginFactory(DimensionEdit,
                                               toolTip='QLineEdit with Sympy unit support and enforced output dimensions')
SymbolEditPlugin = WidgetPluginFactory(SymbolEdit,
                                            toolTip='SympyLabelEdit for creating sympy.Symbol')
SympyEntryWidgetPlugin = WidgetPluginFactory(SympyEntryWidget,
                                             toolTip='SympyLabelEdit and QComboBox for unit conversions')
