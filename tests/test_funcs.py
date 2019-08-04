import pytest
from . import units_convert_check, expr_safe_check, units_work_check
from sympyentrywidget import \
    (expr_is_safe, parseExprUnits,
     parseExpr, unitsAreConsistent, UnitMisMatchError,
     convertTo, unitSubs, check_dimensions, _exprToSymbol,
     getDimension, _keywordError, _invalidIdentifierError,
     _notSafeError, Symbol, units, ExpressionError)
import logging
import sys

testLogger = logging.getLogger('testLogger')
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def test_expr_errors():
    # expr, is_safe, causes parsing error, is valid identifier

    for ex, safe, cause_error, ident in expr_safe_check:
        testLogger.debug(f"ex = {ex}, safe = {safe}, error = {cause_error}, ident = {ident}")
        assert expr_is_safe(ex) == safe

        if not safe:
            with pytest.raises(ExpressionError):
                _notSafeError(ex)
        else:
            assert _notSafeError(ex) is False

        if cause_error:
            with pytest.raises(ExpressionError):
                parseExpr(ex)
        else:
            parseExpr(ex)

        if ident:
            assert _invalidIdentifierError(ex) is False
        else:
            with pytest.raises(ExpressionError):
                _invalidIdentifierError(ex)


def test_unit_consistency():
    # expr, units are compatible

    for ex, compat in units_work_check:
        testLogger.debug((ex, compat))

        if compat is False:
            with pytest.raises(UnitMisMatchError):
                unitsAreConsistent(parseExprUnits(ex))
        else:
            ex = parseExprUnits(ex)
            unitsAreConsistent(ex)
            check_dimensions(ex)

    for ex, _, _, _ in units_convert_check:
        testLogger.debug(ex)
        ex = parseExprUnits(ex)
        assert unitsAreConsistent(ex)
        check_dimensions(ex)


def test_unit_converts():
    # expr, target units, compatible, output

    for ex, target_units, compat, output in units_convert_check:
        testLogger.debug(f"ex = {ex}, target = {target_units}, compat = {compat}")

        ex = parseExprUnits(ex)
        if compat is False:
            with pytest.raises(UnitMisMatchError):
                unitsAreConsistent(ex, target_units)
        else:
            unitsAreConsistent(ex, target_units)
            conv = convertTo(ex, target_units)
            out = parseExprUnits(output)
            assert 0 == (conv-out).simplify().evalf().round(18).evalf()


def test_exprToSymbol(qtbot):
    for ex, safe, cause_error, ident in expr_safe_check:
        testLogger.debug(f"ex = {ex}, safe = {safe}, error = {cause_error}, ident = {ident}")

        if not safe:
            with pytest.raises(ExpressionError):
                _exprToSymbol(ex)
            continue
        if ident:
            assert isinstance(_exprToSymbol(ex), Symbol)


