from generalUtils.sympy_utils import expr_is_safe
from entryWidget import EntryWidget, AutoColorLineEdit, LabelLineEdit
from sympy import Symbol, sympify, Expr
from sympy.physics import units
from sympy.physics.units.util import check_dimensions, dim_simplify, quantity_simplify
from sympy.parsing.sympy_parser import parse_expr, TokenError
from keyword import iskeyword
import logging

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


class UnitMisMatchException(Exception):
    """Unit dimensions in expression are inconsistent."""
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


class _SympyHelper():
    def __init__(self):
        self._expr = None
        self.transformations = []

    def isKeywordError(self):
        if iskeyword(self.text()):
            self.logger.log(logging.DEBUG-1, "Keyword in use")
            return "Keyword in use"
        return False

    def isNotSafeError(self):
        if not expr_is_safe(self.text()):
            self.logger.log(logging.DEBUG-1, "Invalid use of '.'")
            return "Invalid use of '.'"
        return False

    def isNotIdentifierError(self):
        if not self.text().isidentifier():
            self.logger.log(logging.DEBUG-1, "Not a valid identifier")
            return "Not a valid identifier"
        return False

    def isSymbolError(self):
        self.logger.log(logging.DEBUG-1, 'isSymbolError()')
        self._expr = None

        if self.text() == '':
            self.logger.log(logging.DEBUG-1, 'Empty string not a valid Sympy Symbol name')
            return 'Empty string not a valid Sympy Symbol name'

        err = self.isNotSafeError() or self.isKeywordError() or self.isNotIdentifierError()
        if err:
            return err
        else:
            self._expr = Symbol(self.text())
            return False

    def isExprError(self):
        self.logger.log(logging.DEBUG-1, 'isExprError()')
        self._expr = None

        if self.text() == '':
            return None

        err = self.isNotSafeError() or self.isKeywordError()
        if err:
            return err

        try:
            # expr = sympify(self.text() if self.text() else '0', local_dict=unitSubs, evaluate=False, transformations=self.transformations)
            expr = parse_expr(self.text() if self.text() else '0', evaluate=False, local_dict=unitSubs)
        except TokenError as e:
            self.logger.log(logging.DEBUG-1, type(e).__name__)
            return type(e).__name__
        except Exception as e:
            self.logger.debug((type(e), e))
            return e

        try:
            if isinstance(expr, Expr):
                # self.logger.debug("Type Expr")
                expr = expr.evalf()
            # elif isinstance(expr, (float, int, units.Quantity, units.Unit, Symbol)):
            #     self.logger.debug("Type Other")
            else:
                raise Exception(f"expr is not Expr: {type(expr)}{expr}")
        except Exception as e:
            self.logger.debug((type(e), e))
            return e

        try:
            if self.unitsAreConsistent(expr):
                self._expr = expr
                self.logger.log(logging.DEBUG-1, f'expr processed: {expr}')
                return False
        except UnitMisMatchException as e:
            self.logger.log(logging.DEBUG-1, e)
            return e

    def getExpr(self):
        self.logger.log(logging.DEBUG-1, f"getExpr(): '{str(self._expr)}'")
        return self._expr

    def getValue(self):
        if self.getError():
            return None
        return self._expr

    def getSymbols(self):
        rv = self._expr.free_symbols if isinstance(self._expr, Expr) else set()
        self.logger.log(logging.DEBUG-1, f'getSymbols(): {type(self._expr)} {self._expr} -> {rv}')
        return rv

    def getSymbolsDict(self):
        rv = {k.name:k for k in self._expr.free_symbols} if self._expr else dict()
        self.logger.log(logging.DEBUG-1, f'getSymbolsDict(): {type(self._expr)} {self._expr} -> {rv}')
        return rv

    def getExprUnits(self):
        return self.getExpr().atoms(units.Unit)

    def getExprDimensions(self):
        return units.Quantity._collect_factor_and_dimension(self.getExpr())[1]

    def unitsAreConsistent(self, expr, target_units=None):
        self.logger.log(logging.DEBUG-1, f'unitsAreConsistent({expr},{target_units})')
        try:
            f, d = units.Quantity._collect_factor_and_dimension(expr)
        except ValueError as e:
            raise UnitMisMatchException
        else:
            if target_units is not None:
                if isinstance(target_units, str):
                    target_units = unitSubs[target_units]
                self.logger.log(logging.DEBUG-1, (target_units, 'has: ', [(s, s.has(units.Unit)) for s in target_units.atoms()]))
                # if isinstance(target_units, (units.Unit, units.Quantity)):
                if any(s.has(units.Unit) for s in target_units.atoms()):
                    f, td = units.Quantity._collect_factor_and_dimension(target_units)
                    self.logger.log(logging.DEBUG-1, ('td: ', td, td.name, 'd: ', d, d.name))
                    if d.name == 1 or d == td:
                        return True
                    else:
                        raise UnitMisMatchException(f"Unit dimensions are inconsistent: {d, td}")
                else:
                    raise TypeError(f'Unrecognized type {type(target_units)} for {target_units}')
            self.logger.log(logging.DEBUG-1, 'consistent')
            return True


class SympyAutoColorLineEdit(AutoColorLineEdit, _SympyHelper):

    def __init__(self, parent=None, **kwargs):
        _SympyHelper.__init__(self)
        AutoColorLineEdit.__init__(self, parent, **kwargs)

    errorCheck = _SympyHelper.isExprError


class SympyLabelLineEdit(LabelLineEdit, _SympyHelper):

    def __init__(self, parent=None, **kwargs):
        _SympyHelper.__init__(self)
        LabelLineEdit.__init__(self, parent, **kwargs)

    errorCheck = _SympyHelper.isExprError


class SympySymbolLineEdit(LabelLineEdit, _SympyHelper):

    def __init__(self, parent=None, **kwargs):
        _SympyHelper.__init__(self)
        LabelLineEdit.__init__(self, parent, **kwargs)

    errorCheck = _SympyHelper.isSymbolError


class SympyEntryWidget(EntryWidget, _SympyHelper):

    defaultArgs = EntryWidget.defaultArgs.copy()
    defaultArgs.update(options=ComboBoxOptionSets.length)
    errorCheck = _SympyHelper.isExprError

    def __init__(self, parent=None, **kwargs):
        _SympyHelper.__init__(self)
        options = kwargs.pop('options', SympyEntryWidget.defaultArgs['options'])
        if not isinstance(options, dict) and hasattr(options, '__iter__'):
            options = {k:unitSubs[k] for k in options}
        kwargs.update(options=options)
        EntryWidget.__init__(self, parent, **kwargs)

    def unitsAreConsistent(self, expr, target_units=None):
        return _SympyHelper.unitsAreConsistent(self, expr, target_units or self.units())

    def getValue(self):
        if self.getError():
            return None
        return self.convertTo(self.units())

    def convertTo(self, unit):
        if isinstance(unit, str):
            unit = unitSubs[unit]
        u = unit
        if self.getError():
            raise self.getError()
        # expr = self._expr.subs(unitSubs)
        expr = self._expr

        # if expr is not None:
        self.logger.log(logging.DEBUG-1, f'convertTo() {expr}, u {u}')
        if not expr.atoms(units.Unit):
            expr = expr * self.units()
            self.logger.log(logging.DEBUG-1, f'with self.units() {expr}')
            _ret = expr

        if _SympyHelper.unitsAreConsistent(self, expr, u):
            _ret = units.convert_to(expr, u)
        # else:
        #     self.logger.log(logging.DEBUG-1, f'Incompatible Units {u} // {expr}')
        #     raise TypeError(f'Incompatible Units {u} // {expr}')
        # else:
        #     self.logger.log(logging.DEBUG-1, 'return: ' + str(u))
        #     _ret = u
        self.logger.log(logging.DEBUG-1, f'return value: {type(_ret)} {str(_ret)}')
        return _ret

    def getUnits(self):
        return self.comboBox.currentData()
    units = getUnits

    def setSelected(self, unit):
        self.logger.debug(f"setSelected({repr(unit)})")
        ops = self.comboBox.allItems()
        if unit in ops.keys():
            self.logger.log(logging.DEBUG-1, "text")
            self.comboBox.setCurrentText(unit)
        elif unit in ops.values():
            self.logger.log(logging.DEBUG-1, "values")
            self.comboBox.setCurrentIndex(self.comboBox.findData(unit))
        else:
            raise ValueError(f"setUnits('{unit}'): {unit} not in available options {ops}")
    setUnits = setSelected

    def _onOptionChanged(self, text):
        """Called when option list emits currentTextChanged signal.
            Updates self._units to the current QComboBox selection.
        """
        self.logger.log(logging.DEBUG-1, f"_onOptionChanged('{text}')")

        # on initialization, comboBox has problems
        if not hasattr(self, 'comboBox'):
            return

        self.setError(self.errorCheck())


__all__ = ['SympyAutoColorLineEdit', 'SympyLabelLineEdit', 'SympyEntryWidget', 'SympySymbolLineEdit', 'units',
           'unitSubs', 'UnitMisMatchException']
