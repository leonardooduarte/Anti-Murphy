"""Nullable statistical presentation; absence must not appear as zero."""
import math

def stat_value(value,digits=1,suffix=''):
    if value is None:return 'Não calculado'
    try:
        v=float(value)
        return f'{v:.{digits}f}'+suffix if math.isfinite(v) else 'Não calculado'
    except (TypeError,ValueError):return 'Não calculado'
