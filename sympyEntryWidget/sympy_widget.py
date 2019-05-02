from generalUtils.sympy_utils import expr_is_safe
from entryWidget.entry_widget import EntryWidget, AutoColorLineEdit, LabelLineEdit
from sympy import Symbol, sympify, Expr
from sympy.core.sympify import SympifyError
import logging
from tokenize import TokenError
import sympy.physics.units as units
from types import MethodType
from copy import copy
from keyword import iskeyword
from PyQt5.QtWidgets import QWidget

unitSubs = {k:getattr(units, k) for k in units.__dict__.keys() if (isinstance(getattr(units, k), Expr) and getattr(units, k).has(units.Unit))}

def symbolsContainUnits(syms):
    """Detect if iterable of Symbol(s) contains units/physical quantities.

    :param syms: iterable of Symbols or strings to search
    :return: True if something representing a unit is in syms.

        for sym in syms:
            if isinstance(sym, str) and getattr(units, sym, False):
                return True
            elif isinstance(sym, (units.Unit, units.Quantity)):
                return True
            elif isinstance(sym, Symbol) and getattr(units, sym.name, False):
                return True
        return False
    """
    for sym in syms:
        if isinstance(sym, str) and getattr(units, sym, False):
            return True
        elif isinstance(sym, (units.Unit, units.Quantity)):
            return True
        elif isinstance(sym, Symbol) and getattr(units, sym.name, False):
            return True
    return False


class _SympyHelper():
    def __init__(self):
        super().__init__()
        self._expr = None
        self._symbols = set()
        self._evald = None

    def isKeywordError(self):
        if iskeyword(self.text()):
            logging.debug(self.name + "Keyword in use")
            return "Keyword in use"
        return False

    def isNotSafeError(self):
        if not expr_is_safe(self.text()):
            logging.debug(self.name + "Invalid use of '.'")
            return "Invalid use of '.'"
        return False

    def isNotIdentifierError(self):
        if not self.text().isidentifier():
            logging.debug(self.name + "Not a valid identifier")
            return "Not a valid identifier"
        return False

    def isSymbolError(self):
        logging.debug(self.name + 'isSymbolError()')
        self._expr = None
        self._symbols = set()

        if self.text() == '':
            return 'Empty string not a valid Sympy Symbol name'

        err = self.isNotSafeError()
        if err:
            return err

        err = self.isKeywordError()
        if err:
            return err

        err = self.isNotIdentifierError()
        if err:
            return err
        else:
            self._symbols = {Symbol(self.text())}
            return False

    def isExprError(self):
        logging.debug(self.name + 'isExprError()')
        self._expr = None
        self._symbols = set()

        if self.text() == '':
            return False

        err = self.isNotSafeError()
        if err:
            return err

        err = self.isKeywordError()
        if err:
            return err

        try:
            # expr = parse_expr(self.text() if self.text() else '0', evaluate=False, transformations=self.transformations)
            expr = sympify(self.text(), evaluate=False)
        except (SyntaxError, TypeError):
            logging.debug(self.name + 'SyntaxError')
            return 'SyntaxError'
        except AttributeError:
            # TODO: account for globals() containing what is in expr
            logging.debug(self.name + 'AttributeError')
            return 'AttributeError'
        except TokenError:
            logging.debug(self.name + 'TokenError')
            return 'TokenError'
        except SympifyError:
            logging.debug(self.name + 'SympifyError')
            return 'SympifyError'
        else:
            try:
                self._evald = expr.evalf()
            except TypeError:
                logging.debug(self.name + 'TypeError')
                return 'TypeError'
            except AttributeError:
                logging.debug(self.name + 'AttributeError')
                return 'AttributeError'
            else:
                self._expr = expr
                self._symbols = expr.atoms(Symbol)
                logging.debug(self.name + 'expr and symbols set')
                return False

    def getExpr(self):
        logging.debug(self.name + f"getExpr():'{str(self._expr)}'")
        return self._expr

    def getSymbols(self):
        logging.debug(self.name + f'getSymbols():{str(self._symbols)}')
        return copy(self._symbols)

    def getSymbolsDict(self):
        logging.debug(self.name + 'getSymbolsDict()')
        return {k.name:k for k in self._symbols}


class SympyAutoColorLineEdit(AutoColorLineEdit, _SympyHelper):

    def __init__(self, parent=None, **kwargs):
        assert 'isError' not in kwargs.keys(), "Keyword: 'isError' not available for {self.__class__.__name__}"
        AutoColorLineEdit.__init__(self, parent, isError=_SympyHelper.isExprError, **kwargs)

        self.getValue = self.getExpr

        if self.__class__.__name__ == 'SympyAutoColorLineEdit':
            self._inited = True

        self.setError(self.isError())


class SympyLabelLineEdit(LabelLineEdit, _SympyHelper):

    def __init__(self, parent=None, **kwargs):
        assert 'isError' not in kwargs.keys(), "Keyword: 'isError' not available for {self.__class__.__name__}"
        super().__init__(parent, isError=_SympyHelper.isExprError, **kwargs)

        self.getValue = self.getExpr

        if self.__class__.__name__ == 'SympyAutoColorLineEdit':
            self._inited = True

        self.setError(self.isError())


class SympySymbolLineEdit(LabelLineEdit, _SympyHelper):

    def __init__(self, parent=None, **kwargs):
        assert 'isError' not in kwargs.keys(), "Keyword: 'isError' not available for {self.__class__.__name__}"
        kwargs.setdefault('startPrompt','variableName')
        super().__init__(parent, isError=_SympyHelper.isSymbolError, **kwargs)

        self.getValue = self.getExpr

        if self.__class__.__name__ == 'SympySymbolLineEdit':
            self._inited = True

        self.setError(self.isError())


class SympyEntryWidget(EntryWidget, _SympyHelper):

    def __init__(self, parent=None, **kwargs):
        assert 'isError' not in kwargs.keys(), "Keyword: 'isError' not available for {self.__class__.__name__}"
        super().__init__(parent, isError=_SympyHelper.isExprError, **kwargs)

        if self.__class__.__name__ == 'SympyEntryWidget':
            self._inited = True

        self._units = self.__getUnits()

        self.setError(self.isError())

    def getValue(self):
        logging.debug(self.name + 'getValue()')

        u = self.getUnits()
        expr = self._expr

        if expr is not None:
            if symbolsContainUnits(self.getSymbols()):
                expr = units.convert_to(expr.subs(unitSubs), u)
                logging.debug(self.name + 'return converted: ' + str(expr))
                return expr
            logging.debug(self.name + 'return multiplied: ' + str(expr*u))
            return expr * u
        else:
            logging.debug(self.name + 'return Symbol\'d: ' + str(u))
            return u

    def convert_to(self, target_units):
        logging.debug(self.name + f'convert_to({str(target_units)})')
        if isinstance(target_units, str):
            return units.convert_to(self.getValue(), getattr(units, target_units))
        elif isinstance(target_units, units.quantities.Quantity):
            return units.convert_to(self.getValue(), target_units)
        assert False, 'conversion TypeError'

    def getUnits(self):
        return self._units

    def __getUnits(self):
        u = self._selectedOption
        try:
            u = getattr(units, u)
            logging.debug(self.name + 'u is ' + str(u))
        except AttributeError:
            u = Symbol(u)
            logging.debug(self.name + 'u is symbol ' + str(u))
        return u

    def setUnits(self, unit, fixed):
        # TODO: test unit setting
        if isinstance(unit, units.Quantity):
            unit = unit.abbrev
        self.setSelected(unit, fixed)

    def optionChanged(self):
        """Called when option list emits currentIndexChanged signal.
            Updates _selectedOption to the current QComboBox selection.
            Runs attached onOptionChanged(self) callback.

        :return:
        """
        logging.debug(self.name + f"optionChanged:'{self._optionList.currentText()}'")
        self._selectedOption = self._optionList.currentText()

        self._units = self.__getUnits()

        if self._inited:
            self.onOptionChanged.__self__.onOptionChanged()


__all__ = ['SympyAutoColorLineEdit', 'SympyLabelLineEdit', 'SympyEntryWidget', 'SympySymbolLineEdit', 'units',
           'unitSubs', 'symbolsContainUnits']
