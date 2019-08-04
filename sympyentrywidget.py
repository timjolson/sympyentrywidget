from entrywidget import EntryWidget, AutoColorLineEdit, QHBoxLayout, DictComboBox, delegated
from sympy import (Expr, Symbol, sympify, S,
                   sin, cos, sinh, cosh, tan, tanh, exp,
                   asin, acos, asinh, acosh, atan, atanh, atan2)
from sympy.core.function import FunctionClass as Function
from sympy.physics import units
from sympy.physics.units.util import check_dimensions, quantity_simplify
from sympy.parsing.sympy_parser import parse_expr, TokenError
from PyQt5.QtCore import pyqtProperty, pyqtSignal
from keyword import iskeyword
import logging
import re

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__unitsExprs = {k:v for k,v in vars(units).items() if isinstance(v, Expr)}
__dimensions = {k:v for k,v in __unitsExprs.items() if isinstance(v, units.Dimension)}
__lengths = {k:getattr(units, k) for k in units.find_unit(units.inch)}
__areas = {k+'^2':v**2 for k,v in __lengths.items()}
__masses = {k:getattr(units, k) for k in units.find_unit(units.gram)}
__masses.update(lbm=units.pound)
__forces = {k:getattr(units, k) for k in units.find_unit(units.newton)}
lbf = units.Quantity('pound-force', 'lbf')
lbf.set_dimension(units.newton.dimension)
lbf.set_scale_factor(units.pound.scale_factor)
__forces.update(lbf=lbf)
__accelerations = {k:getattr(units, k) for k in units.find_unit(units.gee)}
__volumes = {k:getattr(units, k) for k in units.find_unit(units.liter)}
__volumes.update(USgal=231*units.inch**3, UKgal=4.54609*units.liter)
__volumes.update({k+'^3':v**3 for k,v in __lengths.items()})
__pressures = {k:getattr(units, k) for k in units.find_unit(units.pascal)}
__times = {k:getattr(units, k) for k in units.find_unit(units.minute)}
# __angles = {k:getattr(units, k) for k in units.find_unit(units.radian)}
# __velocities = {k:getattr(units, k) for k in units.find_unit(units.speed)}
# __frequencies = {k:getattr(units, k) for k in units.find_unit(units.hertz)}
# __information = {k:getattr(units, k) for k in units.find_unit(units.byte)}
# __powers = {k:getattr(units, k) for k in units.find_unit(units.power)}
# __voltages = {k:getattr(units, k) for k in units.find_unit(units.volts)}
# __currents = {k:getattr(units, k) for k in units.find_unit(units.ampere)}
# __charges = {k:getattr(units, k) for k in units.find_unit(units.coulomb)}
# __lights = {k:getattr(units, k) for k in units.find_unit(units.luminosity)}
# __resistances = {k:getattr(units, k) for k in units.find_unit(units.ohm)}
# __amounts = {k:getattr(units, k) for k in units.find_unit(units.mol)}
# __temperatures = {k:getattr(units, k) for k in units.find_unit(units.kelvin)}
# __magneticdensities = {k:getattr(units, k) for k in units.find_unit(units.tesla)}
# __magneticfluxes = {k:getattr(units, k) for k in units.find_unit(units.weber)}
# __energies = {k:getattr(units, k) for k in units.find_unit(units.electronvolt)}
# __capacitances = {k:getattr(units, k) for k in units.find_unit(units.farad)}
# __inductances = {k:getattr(units, k) for k in units.find_unit(units.henry)}

unitSubs = unit_subs = dict(__lengths, **__masses, **__forces, **__accelerations, **__volumes, **__pressures, **__times, **__areas)
units.One = S.One
_modded_special_types = (exp, sin, cos, sinh, cosh, tan, tanh, asin, acos, asinh, acosh, atan, atanh, atan2)
dim1 = units.Dimension(1).name
for t in _modded_special_types:
    setattr(t, 'name', dim1)


def expr_is_safe(expr_string):
    """Returns whether the string is safe to 'eval()'.
    Detects improper use of '.' attribute access

    :param expr_string: string to check for safety
    :return: True if safe, False otherwise
    """
    assert isinstance(expr_string, str), 'Provide a string expression to verify is safe'
    for r in '()+-*/':
        expr_string = expr_string.replace(r, " "+r+" ")

    # return re.search(r"((\d*((?=\D)\S)+\d*)+[.])|([.](\d*((?=\D)\S)+))", expr_string) is None
    # return re.search(r"((((?=\D)\S)+\d*)+[.])|([.]\d*((?=[\D])\S)+)", expr_string) is None
    return re.search(r"(((?=\D)\S)+\d*)+[.]|[.]\d*((?=[\D])\S)+", expr_string) is None


class UnitMisMatchError(ValueError):
    """Unit dimensions are inconsistent."""
    pass


class ExpressionError(ValueError):
    pass


class CommonUnits():
    """
    Set of pre-built dicts {key:sympy.physics.units.Quantity}
    dicts:
        length, mass, area, force, acceleration, volume, pressure
    """
    length = {k:unitSubs[k] for k in ['mm', 'cm', 'inch', 'ft', 'yard', 'm']}
    mass = {k:unitSubs[k] for k in ['gram', 'mg', 'lbm', 'kg']}
    area = {k+'^2':unitSubs[k]**2 for k in length.keys()}
    force = {k:unitSubs[k] for k in ['N', 'mg', 'lbf', 'kg']}
    acceleration = {'g':units.gee, 'm/s2':units.m/units.second**2, 'ft/s2':units.feet/units.second**2}
    volume = {k:unitSubs[k] for k in ['ml', 'cl', 'liter', 'quarts', 'USgal']}
    volume.update({k+'^3':unitSubs[k]**3 for k in length.keys()})
    pressure = {k:unitSubs[k] for k in ['Pa', 'kPa', 'atm', 'psi', 'bar', 'mmHg', 'torr']}


def _keywordError(text):
    if iskeyword(text):
        raise ExpressionError("Keyword in use")
    return False


def _notSafeError(text):
    if not expr_is_safe(text):
        raise ExpressionError("Invalid use of '.'")
    return False


def _invalidIdentifierError(text):
    if not text.isidentifier():
        raise ExpressionError("Not a valid identifier")
    return False


def _exprToSymbol(text):
    if text == '':
        raise ExpressionError('Empty string not a valid Sympy Symbol name')

    return _notSafeError(text) or _keywordError(text) or _invalidIdentifierError(text) or Symbol(text)


def parseExpr(text):
    """Parse a string, checking for errors.
    Returns sympy.Expr if all is well, None if text=='',
        otherwise raises sympyentrywidget.ExpressionError

    Notes:
    Replaces `^` with `**` before processing (ease of exponent usage).
    Checks if text is relatively safe to evaluate.

    :param text: str
    :return: sympy.Expr or None
    """
    logger.log(logging.DEBUG - 1, f"parseExpr('{text}')")
    if text == '':
        return None
    text = text.replace('^', '**')
    err = _notSafeError(text) or _keywordError(text)

    try:
        expr = parse_expr(text, evaluate=False)
        str(expr)  # catch some problems
    except AttributeError as e:
        raise ExpressionError("Unknown function call")
    except (TokenError, SyntaxError, TypeError) as e:
        raise ExpressionError("Syntax error")
    except Exception as e:
        raise ExpressionError((type(e).__name__, repr(e)))

    if isinstance(expr, Function):
        raise ExpressionError('Function is not a valid expression')

    return expr


def getDimension(expr):
    """Get the units.Dimension expression of `expr`.
    If the dimension cannot be determined, returns None.

    :param expr: sympy.Expr
    :return: units.Dimension or None
    """
    logger.log(logging.DEBUG-1, f'getDimension({expr})')
    if expr is not None:
        try:
            result = units.Quantity._collect_factor_and_dimension(expr)[1]
        except ValueError as e:
            logger.log(logging.DEBUG-1, f'getDimension() -> {repr(e)}')
            result = None
        except AttributeError as e:
            logger.log(logging.DEBUG-1, f'getDimension() -> {repr(e)}')
            ev = quantity_simplify(expr).evalf()
            result = units.Quantity._collect_factor_and_dimension(ev)[1]
    else:
        result = None
    logger.log(logging.DEBUG-1, f'getDimension({expr}) -> {result}')
    return result


def convertTo(expr, unit):
    """Wraps units.convert_to for extra functionality.

    Extra features:
        Allows `unit` to be a string.
        If `expr` has no units, returns `expr * unit`.

    :param expr: sympy.Expr
    :param unit: str\\units.Quantity\\units.Dimension
    :return: sympy.Expr or None
    """
    logger.log(logging.DEBUG-1, f'convertTo({expr}, {unit})')
    if expr is None:
        return None

    if isinstance(unit, str):
        try:
            unit = unitSubs[unit]
        except KeyError:
            unit = parseExpr(unit)
    u = unit

    logger.log(logging.DEBUG-1, f'convertTo() expr {expr}, u {u}')
    dim = getDimension(expr)
    logger.log(logging.DEBUG - 1, f'convertTo() dim = {dim}')
    if dim is None:
        _ret = expr * u
    if dim is not None and dim.name == 1:
        _ret = expr * u
    else:
        _ret = units.convert_to(expr, u)

    logger.log(logging.DEBUG-1, f'convertTo() -> {str(_ret)}')
    return _ret


def parseExprUnits(text):
    """Parse a string with units possibly included.
    See parseExpr for pre-processing steps.

    Raises ExpressionError same as parseExpr.
    Raises UnitMisMatchError if the expression has incompatible units.

    :param text: str
    :return: sympy.Expr or None
    """
    logger.log(logging.DEBUG - 1, f'parseExprUnits({text})')

    if text == '':
        return None
    text = text.replace('^', '**')
    err = _notSafeError(text) or _keywordError(text)

    try:
        expr = parse_expr(text, evaluate=False, local_dict=unitSubs)
        str(expr)  # catch some problems
    except AttributeError as e:
        raise ExpressionError("Unknown function call")
    except (TokenError, SyntaxError, TypeError) as e:
        raise ExpressionError("Syntax error")
    except Exception as e:
        raise ExpressionError((type(e).__name__, repr(e)))
    if isinstance(expr, Function):
        raise ExpressionError('Function is not a valid expression')

    try:
        expr = quantity_simplify(expr)
    except TypeError:
        pass

    try:
        unitsAreConsistent(expr)
    except UnitMisMatchError as e:
        raise e
    return expr


def unitsAreConsistent(expr, targetUnits=None):
    """Check if an expression's units are compatible.
    If `targetUnits` provided, also checks for compatibility for
    converting to `targetUnits`.

    Raises UnitMisMatchError if `expr` has incompatible or
        indeterminate units, or if `expr` and `targetUnits` are
        not compatible.

    Note: If `expr` has dimension of `1` (unit-less), returns `True`
        barring other errors occur.

    :param expr: sympy.Expr
    :param targetUnits: str\\units.Quantity\\units.Dimension
    :return: True or raises UnitMisMatchError
    """
    logger.log(logging.DEBUG - 1, f'unitsAreConsistent({expr}, {targetUnits})')

    try:
        # rough check within expression
        check_dimensions(expr)
        logger.log(logging.DEBUG-1, f"check_dimensions -> {bool(check_dimensions(expr))}")
    except ValueError as e:
        raise UnitMisMatchError(repr(e))
    except TypeError as e:
        raise UnitMisMatchError(repr(e))

    expr_dim = getDimension(expr)
    logger.log(logging.DEBUG-1, f"expr_dim = {expr_dim}")
    if expr_dim is None:
        raise UnitMisMatchError("Dimension could not be determined")

    if targetUnits is None:
        return True

    # get dimensions of target units
    if isinstance(targetUnits, str):
        try:
            targetUnits = unitSubs[targetUnits]
        except KeyError:
            targetUnits = parseExprUnits(targetUnits)

    target_dim = getDimension(targetUnits)
    logger.log(logging.DEBUG-1, f"target_dim = {target_dim}")

    # compare dimensions
    if expr_dim.name == 1 or expr_dim.name == target_dim.name:
        return True
    else:
        raise UnitMisMatchError(f"{expr_dim} incompatible with {target_dim}")


class SympySymbolEdit(AutoColorLineEdit):
    """entrywidget.AutoColorLineEdit subclass
    Added signals:
        exprChanged([]],[object],[str])  # emitted when the expression is successfully changed

    Added methods:
        getExpr: get the widget's current sympy.Expr (after processing by errorCheck)

    written by Tim Olson - timjolson@user.noreplay.github.com
    """
    exprChanged = pyqtSignal([], [object], [str])

    def __init__(self, parent=None, **kwargs):
        self._expr = None
        AutoColorLineEdit.__init__(self, parent, **kwargs)
        self.exprChanged[object].connect(lambda o: self.exprChanged[str].emit(str(o)))
        self.exprChanged[object].connect(lambda o: self.exprChanged.emit())

    @staticmethod
    def errorCheck(self):
        """Checks if self.text() makes a valid sympy.Symbol.
        Sets self._expr to None or the sympy.Symbol version of self.text().
        Returns applicable error status.

        :return: ExpressionError when relevant
                 False if no error
                 None if resulting expression is None
        """
        self.logger.log(logging.DEBUG-1, f'errorCheck()')
        try:
            expr = _exprToSymbol(self.text())
        except ExpressionError as e:
            self.logger.log(logging.DEBUG-1, f'errorCheck() -> {repr(e)}')
            self._expr = None
            return e

        if expr is None:
            self.logger.log(logging.DEBUG-1, 'errorCheck() -> None')
            self._expr = None
            return None
        self.logger.log(logging.DEBUG-1, 'errorCheck() -> False')
        self._expr = expr
        self.exprChanged[object].emit(expr)
        return False

    def getExpr(self):
        return self._expr

    def getSymbols(self):
        return {str(self._expr):self._expr}


class SympyExprEdit(SympySymbolEdit):
    """entrywidget.AutoColorLineEdit subclass
    Added signals:
        exprChanged([]],[object],[str])  # emitted when the expression is successfully changed
        valueChanged([]],[object],[str])  # same as exprChanged, but emits sympy's evalf(expr)

    Added methods:
        getExpr: get the widget's current sympy.Expr (after processing by errorCheck)
        getValue: uses sympy's evalf on the widget's expression, passing all arguments
        getSymbols: get a dict of the free symbols in widget's expression ; {symbol name:Symbol}

    written by Tim Olson - timjolson@user.noreplay.github.com
    """
    valueChanged = pyqtSignal([], [object], [str])

    def __init__(self, parent=None, **kwargs):
        self._expr = None
        SympySymbolEdit.__init__(self, parent, **kwargs)
        self.valueChanged[object].connect(lambda o: self.valueChanged[str].emit(str(o)))
        self.valueChanged[object].connect(lambda o: self.valueChanged.emit())

    @staticmethod
    def errorCheck(self):
        """Checks if self.text() makes is a valid sympy.Expr.
        Sets self._expr to None or the sympy.Expr version of self.text().
        Returns applicable error status.

        :return: ExpressionError when relevant
                 False if no error
                 None if resulting expression is None
        """
        self.logger.log(logging.DEBUG-1, f'errorCheck()')

        try:
            expr = parseExpr(self.text())
        except ExpressionError as e:
            self.logger.log(logging.DEBUG-1, f'errorCheck() -> {repr(e)}')
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            self._expr = None
            return e

        if expr is None:
            self.logger.log(logging.DEBUG-1, 'errorCheck() -> None')
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            self._expr = None
            return None
        self.logger.log(logging.DEBUG-1, 'errorCheck() -> False')
        try:
            self._expr = expr.simplify()
        except TypeError:
            self._expr = expr
        self.exprChanged[object].emit(self._expr)
        self.valueChanged[object].emit(self._expr.simplify().evalf())
        return False

    def getValue(self, *args, **kwargs):
        """Get the widget's evaluated expression's value.
        All arguments passed to sympy's evalf.

        :param args, kwargs: passed to evalf
        :return: sympy.Expr or None if self._expr is None
        """
        if self._expr is None:
            return None
        return self._expr.evalf(*args, **kwargs)

    def getSymbols(self):
        rv = {k.name: k for k in self._expr.free_symbols} if self._expr else dict()
        return rv


class SympyUnitEdit(SympyExprEdit):
    """SympyExprEdit subclass
    Added signals:
        exprChanged([]],[object],[str])  # emitted when the expression is successfully changed
        valueChanged([]],[object],[str])  # same as exprChanged, but emits sympy's evalf(expr)

    Added methods:
        getExpr: get the widget's current sympy.Expr (after processing by errorCheck)
        getValue: uses sympy's evalf on the widget's expression, passing all arguments
        getSymbols: get a dict of the free symbols in widget's expression ; {symbol name:Symbol}
        getDimension: get units.Dimension of widget's expression
        getMagnitude: get scale\\magnitude\\value of widget's expression without units
        convertTo: convert widget's expression to different units
        getUnits: get units of widget's expression

    written by Tim Olson - timjolson@user.noreplay.github.com
    """
    @staticmethod
    def errorCheck(self):
        """Checks if self.text() makes is a valid sympy.Expr.
        If expression contains units, checks their compatibility.
        Sets self._expr to None or the sympy.Expr version of self.text().
        Returns applicable error status.

        :return: ExpressionError when relevant
                 UnitMisMatchError when relevant
                 False if no error
                 None if resulting expression is None
        """
        self.logger.log(logging.DEBUG-1, f'errorCheck()')
        try:
            expr = parseExprUnits(self.text())
        except (ExpressionError, UnitMisMatchError) as e:
            self.logger.log(logging.DEBUG-1, f'errorCheck() -> {repr(e)}')
            self._expr = None
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            return e

        if expr is None:
            self.logger.log(logging.DEBUG-1, 'errorCheck() -> None')
            self._expr = None
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            return None
        # else:  # no problems
        self.logger.log(logging.DEBUG-1, 'errorCheck() -> False')
        self._expr = quantity_simplify(expr)
        self.exprChanged[object].emit(self._expr)
        self.valueChanged[object].emit(self._expr.simplify().evalf())
        return False

    def getDimension(self):
        """Get the units.Dimension expression of `self`.
        If the dimension cannot be determined, returns None.

        :return: units.Dimension or None
        """
        return getDimension(self._expr)

    def getMagnitude(self):
        """Get the magnitude of `self`s expression without units.
        If self._expr is None (usually means an error), returns None.

        :return: sympy.Expr or None
        """
        if self._expr is not None:
            return self._expr.args[0]
        else:
            return None

    def convertTo(self, unit, eval=False):
        """Wraps units.convert_to for extra functionality.

        Extra features:
            Allows `unit` to be a string.
            If `self`s expression has no units, returns `expr * unit`.

        :param unit: str\\units.Quantity\\units.Dimension
        :param eval: bool, whether to evaluate resulting expression
        :return: sympy.Expr or None
        """
        if self._expr is None:
            return None
        rv = convertTo(self._expr, unit)
        if eval is True:
            return rv.evalf()
        return rv

    def getUnits(self):
        """Get unit Symbols in `self`s expression.
        If self._expr is None (usually means an error), returns None.

        :return: unit.Quantity if there are units
                 `1` if there are no units
                 None if self._expr is None
        """
        if self._expr is not None:
            if self._expr.atoms(units.Quantity):
                return self._expr.args[1]
            else:
                return 1
        else:
            return None


class SympyEntryWidget(EntryWidget):
    """entrywidget.EntryWidget subclass using SympyUnitEdit in place of AutoColorLineEdit.

    Added signals:
        exprChanged([]],[object],[str])  # emitted when SympyUnitEdit expression is successfully changed
        valueChanged([]],[object],[str])  # same as exprChanged, but uses sympy's evalf on expression first

    Added methods:
        getExpr: get SympyUnitEdit's current sympy.Expr
        getValue: uses sympy's evalf on the widget's expression, passing all arguments
        getSymbols: get a dict of the free symbols in widget's expression ; {symbol name:Symbol}
        convertTo: convert widget's expression to different units
        getUnits: get units selected in widget's comboBox
        setUnits: change widget's comboBox units (raise ValueError if `unit` is not an option)

    written by Tim Olson - timjolson@user.noreplay.github.com
    """
    hasError = pyqtSignal([], [object], [str])
    errorChanged = pyqtSignal([], [object], [str])
    errorCleared = pyqtSignal()
    unitsChanged = EntryWidget.dataChanged
    valueChanged = pyqtSignal([], [object], [str])
    exprChanged = pyqtSignal([], [object], [str])

    defaultArgs = EntryWidget.defaultArgs.copy()
    defaultArgs.update(options=CommonUnits.length)

    getSymbols, getExpr, convertTo = delegated.methods('lineEdit', 'getSymbols, getExpr, convertTo')
    getUnits = delegated.methods('comboBox', 'currentData')

    def __init__(self, parent=None, **kwargs):
        options = kwargs.get('options', None)
        if isinstance(options, str):
            options = getattr(CommonUnits, options)
            kwargs.update(options=options)

        self._value = None
        EntryWidget.__init__(self, parent, **kwargs)  # runs setupUi

    def setupUi(self, kwargs):
        options = kwargs.pop('options', self.defaultArgs['options'])
        optionFixed = kwargs.pop('optionFixed', self.defaultArgs['optionFixed'])

        # connect signals to simpler versions
        self.exprChanged[object].connect(lambda o: self.exprChanged[str].emit(str(o)))
        self.exprChanged[object].connect(lambda o: self.exprChanged.emit())
        self.valueChanged[object].connect(lambda o: self.valueChanged[str].emit(str(o)))
        self.valueChanged[object].connect(lambda o: self.valueChanged.emit())
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
            kwargs['errorCheck'] = lambda lineedit: ec(self)
        else:
            kwargs['errorCheck'] = lambda lineedit: self.errorCheck(self)
        self.lineEdit = lineEdit = SympyUnitEdit(parent=self, **kwargs)
        lineEdit.exprChanged[object].connect(self.exprChanged[object].emit)
        lineEdit.errorCleared.connect(self.errorCleared.emit)
        lineEdit.errorChanged[object].connect(self.errorChanged[object].emit)
        lineEdit.hasError[object].connect(self.hasError[object].emit)

        self.comboBox = combo = DictComboBox(parent=self, options=options)
        combo.setDisabled(optionFixed)
        # combo.setSizeAdjustPolicy(DictComboBox.AdjustToContents)
        combo.currentIndexChanged[int].connect(self.optionIndexChanged[int].emit)
        combo.currentTextChanged[str].connect(self._onOptionChanged)
        combo.currentTextChanged[str].connect(self.optionChanged[str].emit)

        layout = QHBoxLayout(self)
        layout.addWidget(lineEdit)
        layout.addWidget(combo)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    @staticmethod
    def errorCheck(self):
        """Checks if self.text() makes is a valid sympy.Expr.
        If expression contains units, checks their compatibility,
            and their convertibility to comboBox's selected units.
        Sets self._expr to None or the sympy.Expr version of self.text().
        Calculates and stores widget's evaluated value.
        Returns applicable error status.

        :return: ExpressionError when relevant
                 UnitMisMatchError when relevant
                 False if no error
                 None if resulting expression is None
        """
        self.logger.log(logging.DEBUG - 1, f'errorCheck() all')
        self._value = None
        self.lineEdit._expr = None

        def emit_error(err):
            self.logger.log(logging.DEBUG - 1, f'errorCheck() -> {repr(err)}')
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            return err

        def emit_none(reason):
            self.logger.log(logging.DEBUG - 1, f'errorCheck() -> {repr(reason)}')
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            return None

        text = self.lineEdit.text()
        if text == '':
            return emit_none('empty text')

        text = text.replace('^', '**')
        try:
            err = _notSafeError(text) or _keywordError(text)
        except ExpressionError as e:
            return emit_error(e)

        try:
            expr = parse_expr(text, evaluate=False, local_dict=unitSubs)
            str(expr)  # catch some problems
        except AttributeError as e:
            err = ExpressionError("Unknown function call")
        except (TokenError, SyntaxError) as e:
            err = ExpressionError("Syntax error")
        except Exception as e:
            err = ExpressionError((type(e).__name__, repr(e)))
        if err is False and isinstance(expr, Function):
            err = ExpressionError('Function is not a valid expression')

        if err:
            return emit_error(err)

        try:
            expr = quantity_simplify(expr)
        except TypeError:
            pass

        try:
            unitsAreConsistent(expr, self.getUnits())
        except UnitMisMatchError as e:
            return emit_error(e)

        self.logger.log(logging.DEBUG - 1, 'errorCheck() -> False')
        expr = convertTo(expr, self.getUnits())
        self.lineEdit._expr = expr
        self._value = expr.evalf()
        self.exprChanged[object].emit(expr)
        self.valueChanged[object].emit(self._value)
        # finish errorCheck, all good
        return False

    def getValue(self, *args, **kwargs):
        """Get the widget's evaluated expression's value.
        :param *args, **kwargs: parameters passed to sympy's evalf()
        :return: sympy.Expr or None if self._value is None
        """
        self.logger.log(logging.DEBUG-1, 'getValue()')
        if self.getExpr() is None:
            return None
        return self.getExpr().evalf(*args, **kwargs)

    def setUnits(self, unit):
        """Set comboBox's selected option. If `unit` not an option,
            raises ValueError.

        :param unit: str\\units.Quantity
        :return:
        """
        self.logger.debug(f"setUnits({repr(unit)})")
        ops = self.comboBox.allItems()
        if unit in ops.keys():
            self.logger.log(logging.DEBUG-1, "setUnits() unit in keys")
            self.comboBox.setCurrentText(unit)
        elif unit in ops.values():
            self.logger.log(logging.DEBUG-1, "setUnits() unit in values")
            self.comboBox.setCurrentIndex(self.comboBox.findData(unit))
        else:
            raise ValueError(f"setUnits('{unit}'): {unit} not in available options {ops}")
    setSelected = setUnits


__all__ = ['SympySymbolEdit', 'SympyExprEdit', 'SympyUnitEdit', 'SympyEntryWidget', 'units',
           'unitSubs', 'UnitMisMatchError', 'ExpressionError', 'unitsAreConsistent', 'parseExpr', 'parseExprUnits',
           'convertTo', 'getDimension', 'CommonUnits']

if __name__ == '__main__':
    from qt_utils.designer import install_plugin_files
    install_plugin_files('sympyentrywidget_designer_plugin.py')
