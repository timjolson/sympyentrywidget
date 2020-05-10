from entrywidget import EntryWidget, AutoColorLineEdit, \
    QHBoxLayout, DictComboBox, delegated
from sympy import (Expr, Symbol, sympify, S,
                   sin, cos, sinh, cosh, tan, tanh, exp,
                   asin, acos, asinh, acosh, atan, atanh, atan2)
from sympy.core.function import FunctionClass as Function
from sympy.physics import units
from sympy.physics.units.util import check_dimensions, quantity_simplify
from sympy.parsing.sympy_parser import parse_expr, TokenError
from PyQt5.QtCore import pyqtProperty, pyqtSignal
from PyQt5 import QtWidgets
from keyword import iskeyword
import logging
import re

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class _storage:
    USgal = units.Quantity('US gallon', 'USgal')
    # units.systems.SI.set_quantity_scale_factor(USgal, 231*units.inch**3)
    # USgal.set_scale_factor(231*units.inch**3)
    # USgal.set_dimension(units.length**3)
    units.systems.SI.set_quantity_dimension(USgal, units.length**3)
    UKgal = units.Quantity('UK gallon', 'UKgal')
    # units.systems.SI.set_quantity_scale_factor(UKgal, 4.54609*units.liter)
    # UKgal.set_scale_factor(4.54609*units.liter)
    # UKgal.set_dimension(units.length**3)
    units.systems.SI.set_quantity_dimension(UKgal, units.length**3)
    lbf = units.Quantity('pound_force', 'lbf')
    # lbf.set_dimension(units.force)
    units.systems.SI.set_quantity_dimension(lbf, units.force)
    # units.systems.SI.set_quantity_scale_factor(lbf, units.pound.scale_factor)
    # lbf.set_scale_factor(units.pound.scale_factor)
    MPa = megapascal = megapascals = units.Quantity('megapascal', 'MPa')
    # MPa.set_dimension(units.pressure)
    units.systems.SI.set_quantity_dimension(MPa, units.pressure)
    # units.systems.SI.set_quantity_scale_factor(MPa, 1000*units.kPa)
    # MPa.set_scale_factor(1000*units.kPa)
    GPa = gigapascal = gigapascals = units.Quantity('gigapascal', 'GPa')
    # GPa.set_dimension(units.pressure)
    units.systems.SI.set_quantity_dimension(GPa, units.pressure)
    # units.systems.SI.set_quantity_scale_factor(GPa, 1e6*units.kPa)
    # GPa.set_scale_factor(1e6*units.kPa)
    kN = kilonewton = kilonewtons = units.Quantity('kilonewton', 'kN')
    # kN.set_dimension(units.force)
    units.systems.SI.set_quantity_dimension(kN, units.force)
    # units.systems.SI.set_quantity_scale_factor(kN, 1000*units.newton)
    # kN.set_scale_factor(1000*units.newton)

    weight = units.force
    density = units.mass/units.volume
    area = units.length**2
    sec = units.second
    min = units.minute
    hr = units.hour
    lbm = units.pound
    distance = units.length
    Hertz = units.hertz
    for k, v in locals().copy().items():
        if isinstance(v, (units.Quantity, units.Dimension)):
            setattr(units, k, v)
            del locals()[k]

    lengths = distances = {k:getattr(units, k) for k in units.find_unit(units.inch)}
    areas = {k + '^2': v ** 2 for k, v in lengths.items()}
    accelerations = {k:getattr(units, k) for k in units.find_unit(units.gee)}
    pressures = {k:getattr(units, k) for k in units.find_unit(units.pascal)}
    masses = {k:getattr(units, k) for k in units.find_unit(units.gram)}
    forces = weights = {k:getattr(units, k) for k in units.find_unit(units.newton)}
    times = {k:getattr(units, k) for k in units.find_unit(units.minute)}
    angles = {k: getattr(units, k) for k in units.find_unit(units.radian)}
    # velocities = {k: getattr(units, k) for k in units.find_unit(units.speed)}
    # frequencies = {k: getattr(units, k) for k in units.find_unit(units.hertz)}
    # information = {k: getattr(units, k) for k in units.find_unit(units.byte)}
    # powers = {k: getattr(units, k) for k in units.find_unit(units.power)}
    # voltages = {k: getattr(units, k) for k in units.find_unit(units.volts)}
    # currents = {k: getattr(units, k) for k in units.find_unit(units.ampere)}
    # charges = {k: getattr(units, k) for k in units.find_unit(units.coulomb)}
    # lights = {k: getattr(units, k) for k in units.find_unit(units.luminosity)}
    # resistances = {k: getattr(units, k) for k in units.find_unit(units.ohm)}
    # amounts = {k: getattr(units, k) for k in units.find_unit(units.mol)}
    # temperatures = {k: getattr(units, k) for k in units.find_unit(units.kelvin)}
    # magneticdensities = {k: getattr(units, k) for k in units.find_unit(units.tesla)}
    # magneticfluxes = {k: getattr(units, k) for k in units.find_unit(units.weber)}
    # energies = {k: getattr(units, k) for k in units.find_unit(units.electronvolt)}
    # capacitances = {k: getattr(units, k) for k in units.find_unit(units.farad)}
    # inductances = {k: getattr(units, k) for k in units.find_unit(units.henry)}

    volumes = {k: getattr(units, k) for k in units.find_unit(units.liter)}
    volumes.update({k + '^3': v ** 3 for k, v in lengths.items()})

    unit_subs = dict()
    for name, d in locals().copy().items():
        if not isinstance(d, dict) or name == 'unit_subs':
            continue
        for k, v in d.items():
            if isinstance(v, (units.Dimension, units.Quantity)):
                unit_subs[k] = v
    del d, k, v
    dimensions = {k: v for k, v in vars(units).items() if isinstance(v, units.Dimension)}
    units.One = S.One


unitSubs = _storage.unit_subs
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
    length = distance = {k:unitSubs[k] for k in ['mm', 'cm', 'inch', 'ft', 'yard', 'm']}
    mass = {k:unitSubs[k] for k in ['gram', 'mg', 'lbm', 'kg']}
    area = {k+'^2':unitSubs[k]**2 for k in length.keys()}
    force = weight = {k:unitSubs[k] for k in ['N', 'kN', 'lbf']}
    acceleration = {'g':units.gee, 'm/s^2':units.m/units.second**2, 'ft/s^2':units.feet/units.second**2}
    volume = {k:unitSubs[k] for k in ['ml', 'cl', 'liter', 'USgal']}
    volume.update({k+'^3':unitSubs[k]**3 for k in length.keys()})
    pressure = {k:unitSubs[k] for k in ['Pa', 'kPa', 'MPa', 'atm', 'psi', 'bar', 'mmHg', 'pa', 'torr']}
    density = dict()
    for m,M in mass.items():
        for v,V in volume.items():
            if v in ['yard^3']:
                continue
            k = '/'.join([m,v])
            density[k] = M/V
    torque = dict()
    for f,F in force.items():
        for d,D in distance.items():
            if d in ['yard']:
                continue
            k = '-'.join([f,d])
            torque[k] = F*D
    moment = torque


def withoutTypes(expr, types):
    """Get `expr` without atoms that are instances of any `types`

    :param expr: sympy.Expr
    :param types: sympy types; ex. sympy.physics.units.Quantity
    :return: sympy.Expr
    """
    if expr.is_number:
        return expr
    terms = [term for term in expr.args if not isinstance(term, types)]
    expr = expr.func(*terms)
    return expr


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


def textToSymbol(text):
    """Get sympy.Symbol version of `text` after
        checking for safety, keyword, identifier.

    :param text: str
    :return: sympy.Symbol or raises ExpressionError
    """
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
    :return: sympy.Expr, None, or raises ExpressionError
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
            result = units.systems.SI._collect_factor_and_dimension(expr)[1]
        except ValueError as e:
            logger.log(logging.DEBUG-1, f'getDimension() -> {repr(e)}')
            result = None
        except AttributeError as e:
            logger.log(logging.DEBUG-1, f'getDimension() -> {repr(e)}')
            ev = quantity_simplify(expr).evalf()
            result = units.systems.SI._collect_factor_and_dimension(ev)[1]
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


def parseUnits(text, dimension=None):
    """Parse a string with units possibly included.
    See parseExpr for pre-processing steps.

    Raises ExpressionError same as parseExpr.
    Raises UnitMisMatchError if the expression has incompatible units.

    :param text: str
    :return: sympy.Expr or None
    """
    logger.log(logging.DEBUG - 1, f'parseUnits({text})')

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
        unitsAreConsistent(expr, dimension)
    except UnitMisMatchError as e:
        raise e
    return expr


def unitsAreConsistent(expr, targetUnits=None):
    """Check if an expression's units are compatible.
    If `targetUnits` provided, also checks for compatibility for
    converting to `targetUnits`.

    Raises UnitMisMatchError when applicable.

    Notes:
    If `targetUnits` is a units.Dimension, requires `expr` to
        evaluate to units with same units.Dimension (eg. must include units in `expr`)
    If `expr` has dimension of `1` (unit-less), returns `True`
        barring other errors or targetUnits being units.Dimension.

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
            targetUnits = parseUnits(targetUnits)

    target_dim = getDimension(targetUnits)
    logger.log(logging.DEBUG-1, f"target_dim = {target_dim}")

    if isinstance(targetUnits, units.Dimension):
        if targetUnits.name == expr_dim.name:
            return True
        else:
            raise UnitMisMatchError(f"{expr_dim} is not specified {target_dim}")

    # compare dimensions
    if expr_dim.name == 1 or expr_dim.name == target_dim.name:
        return True
    else:
        raise UnitMisMatchError(f"{expr_dim} incompatible with {target_dim}")


class SymbolEdit(AutoColorLineEdit):
    """entrywidget.AutoColorLineEdit subclass
    Added signals:
        exprChanged([]],[object],[str])  # emitted when the expression is successfully changed

    Added methods:
        getExpr: get the widget's current sympy.Expr (after processing by errorCheck)
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
            expr = textToSymbol(self.text())
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


class ExprEdit(SymbolEdit):
    """entrywidget.AutoColorLineEdit subclass
    Added signals:
        exprChanged([]],[object],[str])  # emitted when the expression is successfully changed
        valueChanged([]],[object],[str])  # same as exprChanged, but emits sympy's evalf(expr)
        displayValue(str)  # same as valueChanged, but emits str(evalf(4)) for reasonable display

    Added methods:
        getExpr: get the widget's current sympy.Expr (after processing by errorCheck)
        getValue: uses sympy's evalf on the widget's expression, passing all arguments
        getSymbols: get a dict of the free symbols in widget's expression ; {symbol name:Symbol}
    """
    valueChanged = pyqtSignal([], [object], [str])
    displayValue = pyqtSignal(str)

    def __init__(self, parent=None, **kwargs):
        self._expr = None
        SymbolEdit.__init__(self, parent, **kwargs)
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
            self.displayValue.emit('- - -')
            self._expr = None
            return e

        if expr is None:
            self.logger.log(logging.DEBUG-1, 'errorCheck() -> None')
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            self.displayValue.emit('- - -')
            self._expr = None
            return None
        self.logger.log(logging.DEBUG-1, 'errorCheck() -> False')
        try:
            self._expr = expr.simplify()
        except TypeError:
            self._expr = expr
        self.exprChanged[object].emit(self._expr)
        self.valueChanged[object].emit(self._expr.simplify().evalf())
        self.displayValue.emit(str(self._expr.evalf(4)))
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


class UnitEdit(ExprEdit):
    """ExprEdit subclass
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
            expr = parseUnits(self.text())
        except (ExpressionError, UnitMisMatchError) as e:
            self.logger.log(logging.DEBUG-1, f'errorCheck() -> {repr(e)}')
            self._expr = None
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            self.displayValue.emit('- - -')
            return e

        if expr is None:
            self.logger.log(logging.DEBUG-1, 'errorCheck() -> None')
            self._expr = None
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            self.displayValue.emit('- - -')
            return None
        # else:  # no problems
        self.logger.log(logging.DEBUG-1, 'errorCheck() -> False')
        self._expr = quantity_simplify(expr)
        self.exprChanged[object].emit(self._expr)
        self.valueChanged[object].emit(self._expr.simplify().evalf())
        self.displayValue.emit(str(self._expr.evalf(4)))
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


class DimensionEdit(UnitEdit):
    """UnitEdit subclass, with output having an enforced dimension.
    Added methods:
        setDimension: set dimension of widget's output

    written by Tim Olson - timjolson@user.noreplay.github.com
    """
    defaultArgs = UnitEdit.defaultArgs.copy()
    defaultArgs.update(dimension=units.Dimension('length'))

    def __init__(self, parent=None, **kwargs):
        dim = kwargs.pop('dimension', self.defaultArgs['dimension'])
        if isinstance(dim, str):
            if not _notSafeError(dim):
                new_dim = parse_expr(dim.replace('^', '**'), local_dict=_storage.dimensions)
                if not isinstance(new_dim, units.Dimension):
                    raise TypeError(f"Cannot create Dimension from '{dim}'")
                dim = new_dim
        self._dimension = dim
        UnitEdit.__init__(self, parent, **kwargs)

    @staticmethod
    def errorCheck(self):
        """Checks if self.text() makes is a valid sympy.Expr.
        If expression contains units, checks they are compatible with self.dimension.
        Sets self._expr to None or the sympy.Expr version of self.text().
        Returns applicable error status.

        :return: ExpressionError when relevant
                 UnitMisMatchError when relevant
                 False if no error
                 None if resulting expression is None
        """
        self.logger.log(logging.DEBUG-1, f'errorCheck()')
        try:
            expr = parseUnits(self.text(), self._dimension)
        except (ExpressionError, UnitMisMatchError) as e:
            self.logger.log(logging.DEBUG-1, f'errorCheck() -> {repr(e)}')
            self._expr = None
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            self.displayValue.emit('- - -')
            return e

        if expr is None:
            self.logger.log(logging.DEBUG-1, 'errorCheck() -> None')
            self._expr = None
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            self.displayValue.emit('- - -')
            return None
        # else:  # no problems
        self.logger.log(logging.DEBUG-1, 'errorCheck() -> False')
        self._expr = quantity_simplify(expr)
        self.exprChanged[object].emit(self._expr)
        self.valueChanged[object].emit(self._expr.simplify().evalf())
        self.displayValue.emit(str(self._expr.evalf(4)))
        return False

    def setDimension(self, dim):
        """Set the units.Dimension of `self`.
        :return:
        """
        self.logger.debug(f"setDimension({type(dim), dim})")
        if isinstance(dim, str):
            if not _notSafeError(dim):
                new_dim = parse_expr(dim.replace('^', '**'), local_dict=_storage.dimensions)
                if not isinstance(new_dim, units.Dimension):
                    raise TypeError(f"Cannot create Dimension from '{dim}'")
                dim = new_dim
        self._dimension = dim
        self.setError(self.errorCheck(self))

    def getDimension(self):
        """Get the units.Dimension of `self`.
        :return: units.Dimension or None
        """
        return self._dimension
    dimension = pyqtProperty(str, lambda s: str(s.getDimension().name), setDimension)


class SympyEntryWidget(EntryWidget):
    """entrywidget.EntryWidget subclass using UnitEdit in place of AutoColorLineEdit.

    Added signals:
        exprChanged([]],[object],[str])  # emitted when UnitEdit expression is successfully changed
        valueChanged([]],[object],[str])  # same as exprChanged, but uses sympy's evalf on expression first
        displayValue(str)  # same as valueChanged, but emits str(evalf(4)) for reasonable display

    Added methods:
        getExpr: get UnitEdit's current sympy.Expr
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
    displayValue = pyqtSignal(str)

    defaultArgs = EntryWidget.defaultArgs.copy()
    defaultArgs.update(options=CommonUnits.length, label='Label')

    getSymbols, getExpr, convertTo = delegated.methods('lineEdit', 'getSymbols, getExpr, convertTo')
    getUnits = delegated.methods('comboBox', 'currentData')

    def __init__(self, parent=None, **kwargs):
        self._value = None
        EntryWidget.__init__(self, parent, **kwargs)  # runs setupUi

    def setupUi(self, kwargs):
        options = kwargs.pop('options', self.defaultArgs['options'])
        if isinstance(options, str):
            options = getattr(CommonUnits, options)
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
        self.lineEdit = lineEdit = DimensionEdit(parent=self, **kwargs)
        lineEdit.exprChanged[object].connect(self.exprChanged[object].emit)
        lineEdit.errorCleared.connect(self.errorCleared.emit)
        lineEdit.errorChanged[object].connect(self.errorChanged[object].emit)
        lineEdit.hasError[object].connect(self.hasError[object].emit)
        lineEdit.displayValue.connect(self.displayValue.emit)

        self._label = label = QtWidgets.QLabel(parent=self, text=kwargs.pop('label', self.defaultArgs['label']))
        self.output = output = QtWidgets.QLabel(parent=self)

        def formatNum(expr):
            if expr is None:
                return '- - -'
            expr = expr.evalf(4)
            return str(withoutTypes(expr, (units.Dimension, units.Quantity)))
        self.valueChanged[object].connect(lambda o: self.output.setText(formatNum(o)))

        self.comboBox = combo = DictComboBox(parent=self, options=options)
        combo.setDisabled(optionFixed)
        # combo.setSizeAdjustPolicy(DictComboBox.AdjustToContents)
        combo.currentIndexChanged[int].connect(self.optionIndexChanged[int].emit)
        combo.currentTextChanged[str].connect(self._onOptionChanged)
        combo.currentTextChanged[str].connect(self.optionChanged[str].emit)

        layout = QHBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(lineEdit)
        layout.addWidget(output)
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
            self.displayValue.emit('- - -')
            return err

        def emit_none(reason):
            self.logger.log(logging.DEBUG - 1, f'errorCheck() -> {repr(reason)}')
            self.exprChanged[object].emit(None)
            self.valueChanged[object].emit(None)
            self.displayValue.emit('- - -')
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

        u = getDimension(self.getUnits())

        try:
            unitsAreConsistent(expr, u)
        except UnitMisMatchError as e:
            return emit_error(e)

        self.logger.log(logging.DEBUG - 1, 'errorCheck() -> False')
        expr = convertTo(expr, self.getUnits())
        self.lineEdit._expr = expr
        self._value = expr.evalf()
        self.exprChanged[object].emit(expr)
        self.valueChanged[object].emit(self._value)
        self.displayValue.emit(str(expr.evalf(4)))
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

    getLabel, setLabel = delegated.methods('_label', 'text, setText')
    label = pyqtProperty(str, lambda s: s._label.text(), lambda s, t: s._label.setText(t))


__all__ = ['AutoColorLineEdit', 'EntryWidget', 'SymbolEdit', 'ExprEdit', 'UnitEdit', 'DimensionEdit',
           'SympyEntryWidget', 'units', 'unitSubs', 'UnitMisMatchError',
           'ExpressionError', 'unitsAreConsistent', 'parseExpr', 'parseUnits',
           'convertTo', 'getDimension', 'CommonUnits']

if __name__ == '__main__':
    from qt_utils.designer import install_plugin_files
    install_plugin_files('sympyentrywidget_designer_plugin.py')
