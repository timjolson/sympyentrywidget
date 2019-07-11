# sympyEntryWidget
[EntryWidget](https://github.com/timjolson/entrywidget.git) extension with sympy backend to support symbolic/mathematic evaluation and unit conversions.


## Classes:
    
    SympyAutoColorLineEdit  # QLineEdit with automatic colors
    SympyLabelLineEdit  # SympyAutoColorLineEdit with a QLabel on left side
    SympySymbolLineEdit  # SympyAutoColorLineEdit with a QLabel on left side, turns entry into a sympy.Symbol
    SympyEntryWidget  # SympyLabelLineEdit with QComboBox on right side, evaluates and converts expression with selected units

## Installation

    git clone https://github.com/timjolson/sympyentrywidget.git
    pip3 install sympyentrywidget  # (use -e to edit/develop)
    sudo python3 -m sympyentrywidget  # copy QtDesigner plugin file for system-wide use

## SympyEntryWidget

    entrywidget.EntryWidget
    
    Additional methods:
        getValue  # get expression including/converted to the widget's units (returns None if there is an error)
        convertTo(unit)  # takes widget's expression with units and converts to 'unit' (str or sympy.units.Unit)
        getUnits / units  # returns sympy.units.Unit object selected in combobox
        setSelected(unit) / setUnits(unit)  # change combobox selection (str or sympy.units.Unit)

Additional Attributes
    
    UnitMisMatchException  # Exception raised when conversions are not possible
    ComboBoxOptionSets  # sets of options for DictComboBox built of commonly used units
    units  # sympy.units
    unitSubs  # dict of sympy.units.Unit to use in sympy.subs(expr, unitSubs) or sympy.evalf(expr, subs=unitSubs)

Special methods in all classes

    errorCheck  # checks expression for errors (specific errors dependent on class)
    getExpr  # get sympy.Expr version of widget.text() after error handling
    getSymbols  # get set() of sympy.Symbol's in expression
    getSymbolsDict  # get dict() of {symbol.name: sympy.Symbol, ... }
    getExprUnits  # get set() of sympy.units.Unit's in expression
    getExprDimensions  # get simplified dimension of expression (e.g. 'length', 'mass', 'length/time')
    
    # error methods for specific use cases
    isExprError  # checks isNotSafeError, isKeywordError, then tries to evaluate expression
    isKeywordError  # expression is a python keyword 
    isNotSafeError  # unsafe use of attribute access '.'
    isNotIdentifierError  # invalid python 'variable' name
    isSymbolError  # cannot be sympy symbol name
