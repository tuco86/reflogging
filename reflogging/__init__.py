# -*- coding: utf-8 *-*

from . import loggers
from .loggers import RootLogger
import collections

root_logger = RootLogger()
log = root_logger.get_child("reflogging")

import inspect


def deprecated(mf=None, log=log):
    def _decorator(_orig):
        def _func(*a, **kw):
            c = inspect.currentframe()
            p = c.f_back
            log.warn("%s: %s used in %s:%d %s", message, _orig.__name__, p.f_code.co_filename, p.f_lineno, p.f_code.co_name)
            return _orig(*a, **kw)
        return _func

    message = mf if mf and not isinstance(mf, collections.Callable) else "DeprecationWarning"

    if isinstance(mf, collections.Callable):
        return _decorator(mf)
    else:
        return _decorator
