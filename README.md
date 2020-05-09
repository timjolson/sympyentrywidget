# sympyentrywidget
PyQt5 Widgets centered around QLineEdit, with automatic error checking and color changes.

This package is an extension adding a sympy backend to support symbolic/mathematic evaluation and unit conversions.

## Widgets:
    
    AutoColorLineEdit  # QLineEdit with automatic colors
    EntryWidget        # AutoColorLineEdit with DictComboBox[QComboBox] on right side
    SympySymbolEdit    # Turns entry into a sympy.Symbol
    SympyExprEdit      # Evaluates entry mathematically (or into a sympy.Symbol)
    SympyUnitEdit      # Includes sympy.units support // conversion
    SympyEntryWidget   # SympyUnitEdit with QComboBox on right side; evaluates and converts expression to selected units

## Installation

    git clone https://github.com/timjolson/sympyentrywidget.git
    pip3 install sympyentrywidget  # (use -e to edit/develop)
    sudo python3 -m sympyentrywidget  # copy QtDesigner plugin file for system-wide use

## doc strings:

#### AutoColorLineEdit
    A QLineEdit with error checking options and automatic color updates.
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
    :param autoColors: dict of tuples of color strings; see help(setAutoColor) for formatting
    :param colors: tuple of color strings/QColor/rgb tuples; see help(setManualColors) for formatting
    :param readOnly: bool, whether the text box is editable
    :param liveErrorChecking: bool, whether error checking occurs
                after every keystroke (=True) or only after text editing is finished (=False)

#### EntryWidget
    A DictComboBox after an AutoColorLineEdit.
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
    :param autoColors: dict of tuples of color strings; see help(setAutoColor) for formatting
    :param colors: tuple of colors; see help(setManualColors) for formatting
    :param liveErrorChecking: bool, whether error checking occurs
                after every keystroke (=True) or only after text editing is finished (=False)

    DictComboBox kwargs
    :param options: [str, str, ...] or {str:data, str:data, ...}
    :param optionFixed: bool, whether option is fixed or can be changed

#### SympySymbolEdit
    AutoColorLineEdit subclass
    Added signals:
        exprChanged([]],[object],[str])  # emitted when the expression is successfully changed

    Added methods:
        getExpr: get the widget's current sympy.Expr (after processing by errorCheck)

#### SympyExprEdit
    AutoColorLineEdit subclass
    Added signals:
        exprChanged([]],[object],[str])  # emitted when the expression is successfully changed
        valueChanged([]],[object],[str])  # same as exprChanged, but emits sympy's evalf(expr)
        displayValue(str)  # same as valueChanged, but emits str(evalf(4)) for reasonable display

    Added methods:
        getExpr: get the widget's current sympy.Expr (after processing by errorCheck)
        getValue: uses sympy's evalf on the widget's expression, passing all arguments
        getSymbols: get a dict of the free symbols in widget's expression ; {symbol name:Symbol}

#### SympyUnitEdit

    SympyExprEdit subclass
    Added signals:
        exprChanged([]],[object],[str])  # emitted when the expression is successfully changed
        valueChanged([]],[object],[str])  # same as exprChanged, but emits sympy's evalf(expr)
        displayValue(str)  # same as valueChanged, but emits str(evalf(4)) for reasonable display

    Added methods:
        getExpr: get the widget's current sympy.Expr (after processing by errorCheck)
        getValue: uses sympy's evalf on the widget's expression, passing all arguments
        getSymbols: get a dict of the free symbols in widget's expression ; {symbol name:Symbol}
        getDimension: get units.Dimension of widget's expression
        getMagnitude: get scale\\magnitude\\value of widget's expression without units
        convertTo: convert widget's expression to different units
        getUnits: get units of widget's expression

#### SympyEntryWidget
    EntryWidget subclass using SympyUnitEdit in place of AutoColorLineEdit.

    Added signals:
        exprChanged([]],[object],[str])  # emitted when SympyUnitEdit expression is successfully changed
        valueChanged([]],[object],[str])  # same as exprChanged, but uses sympy's evalf on expression first
        displayValue(str)  # same as valueChanged, but emits str(evalf(4)) for reasonable display

    Added methods:
        getExpr: get SympyUnitEdit's current sympy.Expr
        getValue: uses sympy's evalf on the widget's expression, passing all arguments
        getSymbols: get a dict of the free symbols in widget's expression ; {symbol name:Symbol}
        convertTo: convert widget's expression to different units
        getUnits: get units selected in widget's comboBox
        setUnits: change widget's comboBox units (raise ValueError if `unit` not an option)

#### Module Attributes
    
    UnitMisMatchException  # Exception raised when conversions are not possible
    ExpressionError  # Exception raised when an expression is unsafe or contains an error
    CommonUnits  # collection of dicts of commonly used units
    units  # sympy.units
    unitSubs  # dict of sympy.units.Unit to use in sympy.subs(expr, unitSubs) or sympy.evalf(expr, subs=unitSubs)

#### Module Functions

    parseExpr  # Parse a string, checking for errors
    parseExprUnits  # Parse a string with units possibly included
    getDimension  # Get the units.Dimension expression of `expr`
    convertTo  # Wraps units.convert_to for extra functionality
    unitsAreConsistent  # Check if an expression's units are compatible/convertible

#### Special methods in all classes

    errorCheck  # checks expression for errors (specific errors dependent on class)
    getExpr  # get sympy.Expr version of widget.text() after error handling
    getSymbols  # get dict() of {symbol.name: sympy.Symbol, ... }
    
