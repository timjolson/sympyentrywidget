from generalUtils import expr_is_safe
from entryWidget.entry_widget import EntryWidget, AutoColorLineEdit, LabelLineEdit
from sympy import Symbol, sympify, Expr
from sympy.core.sympify import SympifyError
import logging
from tokenize import TokenError
import sympy.physics.units as units
from types import MethodType
from copy import copy
from keyword import iskeyword

unit_subs = {k:getattr(units, k) for k in units.__dict__.keys() if (isinstance(getattr(units, k), Expr) and getattr(units, k).has(units.Unit))}

def symbols_contain_units(syms):
    """Detect if iterable of Symbol(s) contains units/physical quantities.

    :param syms: iterable of Symbols or strings to search
    :return: True if any sym in syms:
        isinstance(units.Unit)
        isinstance(units.Quantity)
        isinstance(Symbol) and sym.name in units.__dict__
    """
    for sym in syms:
        if isinstance(sym, str):
            if getattr(units, sym, False):
                return True
        elif isinstance(sym, (units.Unit, units.Quantity)):
            return True
        elif isinstance(sym, Symbol):
            if getattr(units, sym.name, False):
                return True
    return False


class SympyHelper():

    def __init__(self, parent=None, **kwargs):
        for k,v in kwargs.items():
            assert k in self.defaultArgs.keys(), f"Keyword: '{k}' not available for {self.__class__.__name__}"

        # self.transformations = (standard_transformations + (implicit_multiplication_application, ))
        # self.transformations = standard_transformations

        self._expr = None
        self._symbols = set()

        for a in ['getExpr', 'getSymbols', 'getSymbolsDict']:
            setattr(self, a, MethodType(getattr(SympyHelper, a), self))

        if 'isError' in kwargs.keys():
            super(type(self), self).__init__(parent, isError=kwargs.pop('isError'), **kwargs)
        else:
            setattr(self, '_isError', MethodType(getattr(SympyHelper, '_isError'), self))
            super(type(self), self).__init__(parent, isError=self._isError, **kwargs)

        self.setError(self._isError())

    def _isError(self):
        logging.debug(self.name + 'isError()')
        self._expr = None
        self._symbols = set()

        if not expr_is_safe(self.text()):
            logging.debug(self.name + "Invalid use of '.'")
            return "Invalid use of '.'"

        if iskeyword(self.text()):
            logging.debug(self.name + "Keyword in use")
            return "Keyword in use"

        if self.text() == '':
            return False

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
                expr.evalf()
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


class SympyAutoColorLineEdit(AutoColorLineEdit):

    def __init__(self, parent=None, **kwargs):
        assert 'isError' not in kwargs.keys(), "Keyword: 'isError' not available for {self.__class__.__name__}"
        SympyHelper.__init__(self, parent, **kwargs)

        self.getValue = self.getExpr

        if self.__class__.__name__ == 'SympyAutoColorLineEdit':
            self._inited = True
            logging.debug(self.name + "---- Initialized ----")


class SympyLabelLineEdit(LabelLineEdit):

    def __init__(self, parent=None, **kwargs):
        assert 'isError' not in kwargs.keys(), "Keyword: 'isError' not available for {self.__class__.__name__}"
        SympyHelper.__init__(self, parent, **kwargs)

        self.getValue = self.getExpr

        if self.__class__.__name__ == 'SympyAutoColorLineEdit':
            self._inited = True
            logging.debug(self.name + "---- Initialized ----")


class SympySymbolLineEdit(LabelLineEdit):

    def __init__(self, parent=None, **kwargs):
        assert 'isError' not in kwargs.keys(), "Keyword: 'isError' not available for {self.__class__.__name__}"
        kwargs.setdefault('startPrompt','variableName')
        SympyHelper.__init__(self, parent, isError=self._isError, **kwargs)

        self.getValue = self.getExpr

        if self.__class__.__name__ == 'SympySymbolLineEdit':
            self._inited = True
            logging.debug(self.name + "---- Initialized ----")

    def _isError(self):
        logging.debug(self.name + 'isError()')
        self._expr = None
        self._symbols = set()

        text = self.text()

        if not expr_is_safe(text):
            logging.debug(self.name + "Invalid use of '.'")
            return "Invalid use of '.'"

        # TODO: do keyword and eval checking

        if self.text().isidentifier():
            self._symbols = {Symbol(self.text())}
            return False
        else:
            logging.debug(self.name + 'Not a valid identifier')
            return 'Not a valid identifier'


class SympyEntryWidget(EntryWidget):

    def __init__(self, parent=None, **kwargs):
        assert 'isError' not in kwargs.keys(), "Keyword: 'isError' not available for {self.__class__.__name__}"
        SympyHelper.__init__(self, parent, **kwargs)

        if self.__class__.__name__ == 'SympyEntryWidget':
            self._inited = True
            logging.debug(self.name + "---- Initialized ----")

        self._units = self.getUnits()

    def getValue(self):
        logging.debug(self.name + 'getValue()')

        u = self.getUnits()
        expr = self._expr

        if expr is not None:
            if symbols_contain_units(self.getSymbols()):
                expr = units.convert_to(expr.subs(unit_subs), u)
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

        u = self._selectedOption
        try:
            u = getattr(units, u)
            logging.debug(self.name + 'u is ' + str(u))
        except AttributeError:
            u = Symbol(u)
            logging.debug(self.name + 'u is symbol ' + str(u))
        self._units = u

        if self._inited:
            self.onOptionChanged.__self__.onOptionChanged()


__all__ = ['SympyAutoColorLineEdit', 'SympyLabelLineEdit', 'SympyEntryWidget', 'SympySymbolLineEdit', 'units', 'unit_subs', 'symbols_contain_units']
