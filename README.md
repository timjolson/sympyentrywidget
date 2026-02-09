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

To install for normal use (from PyPI or system packages):

```sh
pip install -r requirements.txt
```

## Developer Setup

If you are developing `sympyentrywidget` and its dependencies (`entrywidget`, `delegated`, `qt_utils`) at the same time (e.g., as submodules or local clones), use the development requirements file:

```sh
git clone https://github.com/timjolson/entrywidget.git
git clone https://github.com/timjolson/delegated.git
git clone https://github.com/timjolson/qt_utils.git
pip install -r requirements-dev.txt
```

This ensures that changes to those packages are immediately available in your development environment.

## doc strings:

#### AutoColorLineEdit
    See entrywidget package.

#### EntryWidget
    See entrywidget package.

#### SympySymbolEdit
    AutoColorLineEdit subclass
    Added signals:
        exprChanged([],[object],[str])  # emitted when the expression is successfully changed

    Added methods:
        getExpr: get the widget's current sympy.Expr (after processing by errorCheck)

#### SympyExprEdit
    AutoColorLineEdit subclass
    Added signals:
        exprChanged([],[object],[str])  # emitted when the expression is successfully changed
        valueChanged([],[object],[str])  # same as exprChanged, but emits sympy's evalf(expr)
        displayValue(str)  # same as valueChanged, but emits str(evalf(4)) for reasonable display

    Added methods:
        getExpr: get the widget's current sympy.Expr (after processing by errorCheck)
        getValue: uses sympy's evalf on the widget's expression, passing all arguments
        getSymbols: get a dict of the free symbols in widget's expression ; {symbol name:Symbol}

#### SympyUnitEdit

    SympyExprEdit subclass
    Added signals:
        exprChanged([],[object],[str])  # emitted when the expression is successfully changed
        valueChanged([],[object],[str])  # same as exprChanged, but emits sympy's evalf(expr)
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
        exprChanged([],[object],[str])  # emitted when SympyUnitEdit expression is successfully changed
        valueChanged([],[object],[str])  # same as exprChanged, but uses sympy's evalf on expression first
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

## License

See [LICENSE](LICENSE) for details.
