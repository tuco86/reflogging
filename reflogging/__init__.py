# -*- coding: utf-8 *-*

import loggers
from loggers import RootLogger

root_logger = RootLogger()
log = root_logger.get_child("reflogging")

import inspect

def deprecated(mf=None, log=log):
    def _decorator(_orig):
        def _func(*a, **kw):
            c = inspect.currentframe()
            p = c.f_back
            log.warn("%s: %s used in %s:%d %s", message, _orig.func_name, p.f_code.co_filename, p.f_lineno, p.f_code.co_name)
            return _orig(*a, **kw)
        return _func

    message = mf if mf and not callable(mf) else "DeprecationWarning"

    if callable(mf):
        return _decorator(mf)
    else:
        return _decorator
