"""AM-11: finite arithmetic and precise metrics, with legacy-result fallback.

Rounded result keys remain presentation-compatible. Numerical consumers use
``metric``; positive values never become zero solely through display rounding.
No physical time/capacity denominator is replaced by an arbitrary minimum.
"""
from decimal import Decimal, localcontext
import math
import sys


def finite(value, label='valor'):
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f'{label}: informe um número finito.') from exc
    if not math.isfinite(number):
        raise ValueError(f'{label}: informe um número finito.')
    return number


def metric(result, key, default=None):
    """Read unrounded metrics, including plain JSON and older saved results."""
    return finite((result.get('precise') or {}).get(key, result.get(key, default)), key)


def present(value, digits):
    """Retain established rounding, but do not publish a false physical zero."""
    value = finite(value)
    rounded = round(value, digits)
    return value if rounded == 0 and value != 0 else rounded


def product_ratio(numerators, denominators, label, *, zero_over_zero=False):
    """Nonnegative physical products/ratios; Decimal only for extreme floats.

    Recover representable answers after an intermediate overflow/underflow.
    Reject final answers outside float representation rather than inventing a
    duration, rate or capacity. 0/0 is defined only for unused capacity metrics.
    """
    nums = [finite(x, label) for x in numerators]
    dens = [finite(x, label) for x in denominators]
    if any(x < 0 for x in nums + dens):
        raise ValueError(f'{label}: valores negativos não são permitidos.')
    if any(x == 0 for x in dens):
        if zero_over_zero and any(x == 0 for x in nums):
            return 0.0
        raise ValueError(f'{label}: denominador nulo.')
    if any(x == 0 for x in nums):
        return 0.0
    numerator = math.prod(nums)
    denominator = math.prod(dens)
    intermediate_loss = any(not math.isfinite(x) or x < sys.float_info.min
                            for x in (numerator, denominator))
    try:
        answer = numerator / denominator
    except (ZeroDivisionError, OverflowError):
        answer = float('nan')
    if intermediate_loss or not math.isfinite(answer) or answer <= 0:
        with localcontext() as context:
            context.prec = 60
            answer_decimal = Decimal(1)
            for x in nums:
                answer_decimal *= Decimal.from_float(x)
            for x in dens:
                answer_decimal /= Decimal.from_float(x)
            answer = float(answer_decimal)
    if not math.isfinite(answer) or answer <= 0:
        raise ValueError(f'{label}: resultado fora da representação numérica finita.')
    return answer
