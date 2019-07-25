from entrywidget import EntryWidget, AutoColorLineEdit, QHBoxLayout, DictComboBox, delegated
from sympy import Symbol, sympify, Expr
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
__forces.update(lbf=units.pound*units.gee)
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

unitSubs = dict(__lengths, **__masses, **__forces, **__accelerations, **__volumes, **__pressures, **__times, **__areas)


def expr_is_safe(expr_string):
    """Returns whether the string is safe to 'eval()'.
    Detects improper use of '.' attribute access

    :param expr_string: string to check for safety
    :return: True if safe, False otherwise
    """
    assert isinstance(expr_string, str), 'Provide a string expression to verify is safe'
    string = 'expr_string'
    for r in '()+-*/':
        if r in expr_string:
            string += ".replace('" + r + "', ' " + r + " ')"
    expr_string = eval(string, globals(), {'expr_string':expr_string})

    # return re.search(r"((\d*((?=\D)\S)+\d*)+[.])|([.](\d*((?=\D)\S)+))", expr_string) is None
    # return re.search(r"((((?=\D)\S)+\d*)+[.])|([.]\d*((?=[\D])\S)+)", expr_string) is None
    return re.search(r"(((?=\D)\S)+\d*)+[.]|[.]\d*((?=[\D])\S)+", expr_string) is None


# sample expressions to test
# ( expr, is_safe, causes error in sympy widgets, is valid identifier(variable name) )
expr_safe_check = [
    ('.a ', False, True, False),
    ('abc', True, False, True),
    ('1.1)', True, True, False),
    ('a)', True, True, False),
    ('1234a.', False, True, False),
    ('12a.a', False, True, False),
    ('1.a ', False, True, False),
    ('a.1 ', False, True, False),
    ('12a12.', False, True, False),
    ('2+4.1', True, False, False),
    ('a.a ', False, True, False),
    ('12a12.12a', False, True, False),
    ('.1 ', True, False, False),
    ('a.a', False, True, False),
    ('.a12', False, True, False),
    ('12a12.12', False, True, False),
    ('1212.a', False, True, False),
    ('ab.ab ', False, True, False),
    ('1212.12a', False, True, False),
    ('.ab ', False, True, False),
    ('a', True, False, True),
    ('.12a', False, True, False),
    ('1.ab ', False, True, False),
    ('error', True, False, True),
    ('ab.1 ', False, True, False),
    ('(a', True, True, False),
    ('1.1 ', True, False, False),
    ('a. ', False, True, False),
    ('12.12a', False, True, False),
    ('1. ', True, False, False),
    ('', True, False, False),
    ('ab. ', False, True, False),
    ('ab.', False, True, False),
    ('text', True, False, True),
    ('text_2', True, False, True),
    ('text2', True, False, True),
    ('text2a', True, False, True),
    ('text2.', False, True, False),
    ('(.1)', True, False, False),
    ('(1.)', True, False, False),
    ('1.)', True, True, False),
]


class UnitMisMatchException(Exception):
    """Unit dimensions in expression are inconsistent."""
    pass


class ExpressionError(ValueError):
    pass


class ComboBoxOptionSets():
    length = {k:unitSubs[k] for k in ['mm', 'cm', 'inch', 'ft', 'yard', 'm']}
    mass = {k:unitSubs[k] for k in ['gram', 'mg', 'lbm', 'kg']}
    area = {k+'^2':unitSubs[k]**2 for k in length.keys()}
    force = {k:unitSubs[k] for k in ['N', 'mg', 'lbf', 'kg']}
    acceleration = {'g':units.gee, 'm/s2':units.m/units.second**2, 'ft/s2':units.feet/units.second**2}
    volume = {k:unitSubs[k] for k in ['ml', 'cl', 'liter', 'quarts', 'USgal']}
    volume.update({k+'^3':unitSubs[k]**3 for k in length.keys()})
    pressure = {k:unitSubs[k] for k in ['Pa', 'kPa', 'atm', 'psi', 'bar', 'mmHg', 'torr']}


class _SympyMethods():
    @staticmethod
    def isKeywordError(text):
        if iskeyword(text):
            raise ExpressionError("Keyword in use")
        return False

    @staticmethod
    def isNotSafeError(text):
        if not expr_is_safe(text):
            raise ExpressionError("Invalid use of '.'")
        return False

    @staticmethod
    def isNotIdentifierError(text):
        if not text.isidentifier():
            raise ExpressionError("Not a valid identifier")
        return False

    @staticmethod
    def exprToSymbol(text):
        logger.log(logging.DEBUG - 1, f'exprToSymbol({text})')

        if text == '':
            # logger.log(logging.DEBUG - 1, 'Empty string not a valid Sympy Symbol name')
            raise ExpressionError('Empty string not a valid Sympy Symbol name')

        err = _SympyMethods.isNotSafeError(text) or _SympyMethods.isKeywordError(text) or _SympyMethods.isNotIdentifierError(text)
        return Symbol(text)

    @staticmethod
    def processExpr(text):
        logger.log(logging.DEBUG - 1, f'processExpr({text})')

        if text == '':
            return None

        err = _SympyMethods.isNotSafeError(text) or _SympyMethods.isKeywordError(text)

        try:
            # expr = sympify(self.text() if self.text() else '0', local_dict=unitSubs, evaluate=False, transformations=self.transformations)
            expr = parse_expr(text if text else '0', evaluate=False, local_dict=unitSubs)
        except AttributeError as e:
            raise ExpressionError("Unknown function call")
        except Exception as e:
            raise ExpressionError(type(e).__name__)

        try:
            if isinstance(expr, Expr):
                expr = expr.evalf()
            else:
                raise ExpressionError(f"processExpr() expr is not Expr: {type(expr)} {expr}")
        except Exception as e:
            raise ExpressionError(repr(e))
        else:
            logger.debug(f"processExpr() returning {type(expr)} {expr}")
            return expr

    @staticmethod
    def processExprUnits(text):
        logger.log(logging.DEBUG - 1, f'processExprUnits({text})')

        if text == '':
            return None

        try:
            expr = _SympyMethods.processExpr(text)
        except ExpressionError as e:
            # logger.debug(f'processExprUnits() expr exception {e}')
            raise e

        try:
            _SympyMethods.unitsAreConsistent(expr)
        except UnitMisMatchException as e:
            # logger.debug(f'processExprUnits() units exception {e}')
            raise e
        return expr.simplify()

    @staticmethod
    def unitsAreConsistent(expr, target_units=None):
        logger.log(logging.DEBUG-1, f'unitsAreConsistent({expr}, {target_units})')
        try:
            # TODO: rewrite to use check_dimension(expr)
            f, d = units.Quantity._collect_factor_and_dimension(expr)
        except ValueError as e:
            raise UnitMisMatchException(f"Expression dimensions are inconsistent")
        else:
            if target_units is not None:
                if isinstance(target_units, str):
                    target_units = unitSubs[target_units]
                # logger.log(logging.DEBUG-1, (target_units, 'has: ', [(s, s.has(units.Unit)) for s in target_units.atoms()]))

                # TODO: rewrite to use check_dimension(expr)
                # if isinstance(target_units, (units.Unit, units.Quantity)):
                if any(s.has(units.Unit) for s in target_units.atoms()):
                    try:
                        f, td = units.Quantity._collect_factor_and_dimension(target_units)
                    except ValueError as e:
                        raise UnitMisMatchException(e)

                    # logger.log(logging.DEBUG-1, ('td: ', td, td.name, 'd: ', d, d.name))
                    if d.name == 1 or d == td:
                        pass
                    else:
                        raise UnitMisMatchException(f"Unit dimensions are inconsistent: {d, td}")
                else:
                    raise TypeError(f'Unrecognized type {type(target_units)} for {target_units}')
            logger.log(logging.DEBUG-1, 'consistent')
            return True


class SympySymbolEdit(AutoColorLineEdit):
    exprChanged = pyqtSignal([], [object], [str])

    def __init__(self, parent=None, **kwargs):
        self._expr = None
        AutoColorLineEdit.__init__(self, parent, **kwargs)
        self.exprChanged[object].connect(lambda o: self.exprChanged[str].emit(str(o)))
        self.exprChanged[object].connect(lambda o: self.exprChanged.emit())

    def errorCheck(self):
        self.logger.debug(f'errorCheck()')
        try:
            expr = _SympyMethods.exprToSymbol(self.text())
        except ExpressionError as e:
            self.logger.debug(f'errorCheck() -> {repr(e)}')
            self._expr = None
            return e
        else:
            if expr is None:
                self.logger.debug('errorCheck() -> None')
                self._expr = None
                return None
            self.logger.debug('errorCheck() -> False')
            self._expr = expr
            self.exprChanged[object].emit(expr)
            return False

    def getExpr(self):
        return self._expr


class SympyExprEdit(SympySymbolEdit):
    def errorCheck(self):
        self.logger.debug(f'errorCheck()')

        try:
            expr = _SympyMethods.processExpr(self.text())
        except ExpressionError as e:
            self.logger.debug(f'errorCheck() -> {repr(e)}')
            self._expr = None
            return e
        else:
            if expr is None:
                self.logger.debug('errorCheck() -> None')
                self._expr = None
                return None
            self.logger.debug('errorCheck() -> False')
            self._expr = expr
            self.exprChanged[object].emit(expr)
            return False

    def getSymbols(self):
        rv = self._expr.free_symbols if isinstance(self._expr, Expr) else set()
        self.logger.log(logging.DEBUG - 1, f'getSymbols(): {type(self._expr)} {self._expr} -> {rv}')
        return rv

    def getSymbolsDict(self):
        rv = {k.name: k for k in self._expr.free_symbols} if self._expr else dict()
        self.logger.log(logging.DEBUG - 1, f'getSymbolsDict(): {type(self._expr)} {self._expr} -> {rv}')
        return rv


class SympyUnitEdit(SympyExprEdit):
    def unitsAreConsistent(self, *a, **k):
        return _SympyMethods.unitsAreConsistent(*a, **k)

    def errorCheck(self):
        self.logger.debug(f'errorCheck()')
        try:
            expr = _SympyMethods.processExprUnits(self.text())
        except (ExpressionError, UnitMisMatchException) as e:
            self.logger.debug(f'errorCheck() {repr(e)}')
            self._expr = None
            return e
        else:
            if expr is None:
                self.logger.debug('errorCheck() -> None')
                self._expr = None
                return None
            self.logger.debug('errorCheck() -> False')
            self._expr = expr
            self.exprChanged[object].emit(expr)
        return False

    def getValue(self, *args, **kwargs):
        if self._expr is None:
            return None
        return self._expr.evalf(*args, **kwargs)

    def getExprUnits(self):
        expr = self.getExpr()
        if expr is not None:
            return expr.atoms(units.Unit)
        return set()

    def getExprDimensions(self):
        return units.Quantity._collect_factor_and_dimension(self.getExpr())[1]

    def convertTo(self, unit):
        if isinstance(unit, str):
            unit = unitSubs[unit]
        u = unit
        if self.getError():
            raise self.getError()
        expr = self.getValue()

        if expr is None:
            return None

        self.logger.log(logging.DEBUG-1, f'convertTo() {expr}, u {u}')
        if self.unitsAreConsistent(expr, u):
            _ret = units.convert_to(expr, u)

        self.logger.log(logging.DEBUG-1, f'return value: {type(_ret)} {str(_ret)}')
        return _ret


class SympyEntryWidget(EntryWidget):
    valueChanged = pyqtSignal([], [object], [str])

    defaultArgs = EntryWidget.defaultArgs.copy()
    defaultArgs.update(options=ComboBoxOptionSets.length)

    getExprUnits, getExprDimensions = delegated.methods('lineEdit', 'getExprUnits, getExprDimensions')
    getSymbols, getSymbolsDict, getExpr = delegated.methods('lineEdit', 'getSymbols, getSymbolsDict, getExpr')
    exprChanged = delegated.attribute('lineEdit', 'exprChanged')

    getUnits = delegated.methods('comboBox', 'currentData')

    def __init__(self, parent=None, **kwargs):
        options = kwargs.pop('options', SympyEntryWidget.defaultArgs['options'])
        if isinstance(options, str):
            options = getattr(ComboBoxOptionSets, options)
        kwargs.update(options=options)
        EntryWidget.__init__(self, parent, **kwargs)

    def setupUi(self, kwargs):
        options = kwargs.pop('options', self.defaultArgs['options'])
        optionFixed = kwargs.pop('optionFixed', self.defaultArgs['optionFixed'])

        # connect custom signals to simpler versions
        self.valueChanged[object].connect(lambda o: self.valueChanged[str].emit(str(o)))
        self.valueChanged[object].connect(lambda o: self.valueChanged.emit())
        self.optionChanged[str].connect(lambda o: self.optionChanged.emit())
        self.optionIndexChanged[int].connect(lambda o: self.optionIndexChanged.emit())

        self.logger = logging.getLogger(self.name)
        self.logger.addHandler(logging.NullHandler())

        ec = kwargs.pop('errorCheck', None)
        self.lineEdit = lineEdit = SympyUnitEdit(parent=self, **kwargs)
        # set errorCheck after construction to prevent errors
        self.lineEdit.errorCheck = self.errorCheck if ec is None else (lambda: ec(self))

        self.comboBox = combo = DictComboBox(parent=self, options=options)
        combo.setDisabled(optionFixed)
        # combo.setSizeAdjustPolicy(DictComboBox.AdjustToContents)
        combo.currentIndexChanged[int].connect(self.optionIndexChanged[int].emit)
        combo.currentTextChanged[str].connect(self.optionChanged[str].emit)
        combo.currentTextChanged[str].connect(self._onOptionChanged)

        layout = QHBoxLayout(self)
        layout.addWidget(lineEdit)
        layout.addWidget(combo)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    def errorCheck(self):
        self.logger.debug('errorCheck() all')
        err = SympyUnitEdit.errorCheck(self)
        if err:
            self.logger.debug(f'errorCheck() LineEdit -> {err}')
            return err

        expr = self.getExpr()
        try:
            self.lineEdit.unitsAreConsistent(expr, self.getUnits())
        except UnitMisMatchException as e:
            self.logger.debug(f'errorCheck() {type(e), e}')
            return e
        self.lineEdit._expr = expr
        self.valueChanged[object].emit(self.getValue())
        return False

    def getValue(self):
        self.logger.debug('getValue()')
        if self.getError():
            self.logger.debug('getValue() -> None')
            return None
        v = self.convertTo(self.getUnits())
        self.logger.debug(f'getValue() -> {v}')
        return v

    def convertTo(self, unit):
        if isinstance(unit, str):
            unit = unitSubs[unit]
        u = unit
        err = self.getError()
        self.logger.debug(f"convertTo('{unit}') error='{err}'")
        if err:
            raise err
        expr = self.lineEdit.getExpr()

        if expr is None:
            return None

        self.logger.log(logging.DEBUG-1, f'convertTo() {expr}, u {u}')
        if not expr.atoms(units.Unit):
            expr = expr * self.getUnits()
            self.logger.log(logging.DEBUG-1, f'convertTo() with self.units() {expr}')
            _ret = expr

        if _SympyMethods.unitsAreConsistent(expr, u):
            _ret = units.convert_to(expr, u)

        self.logger.log(logging.DEBUG-1, f'convertTo() -> {type(_ret)} {str(_ret)}')
        return _ret

    def setSelected(self, unit):
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
    setUnits = setSelected


__all__ = ['SympyExprEdit', 'SympyEntryWidget', 'SympySymbolEdit', 'units',
           'unitSubs', 'UnitMisMatchException']

if __name__ == '__main__':
    from qt_utils.designer import install_plugin_files
    install_plugin_files('sympyentrywidget_designer_plugin.py')
