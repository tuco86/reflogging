
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class RootLogger():

    def __init__(self):
        self._app_name = None
        self._log_level = 30
        self._handlers = []

    def set_level(self, level):
        assert level in (10, 20, 30, 40, 50),\
            'Level(%s) has to be in (10, 20, 30, 40, 50)' % (level,)
        self._log_level = level

    def set_app_name(self, name):
        self._app_name = name

    def add_handler(self, handler):
        self._handlers.append(handler)

    def get_child(self, name):
        return Logger(name)

    def log(self, severity, name, refs, format, *a, **kw):
        executed_refs = [(n, l(i)) for n, i, l in refs]
        executed_refs = [(n, v) for n, v in executed_refs if v is not None]
        for handler in self._handlers:
            if severity >= handler._log_level:
                handler.record(severity, name, executed_refs, format, *a, **kw)

root_logger = RootLogger()

class Logger():

    def __init__(self, name):
        self._name = name

    def get_instance(self, instance, refs=[]):
        return InstanceLogger(self._name, instance, refs)

    def get_child(self, name):
        return Logger(self._name + '.' + name)

    def debug(self, format, *a, **kw):
        """DEBUG: Info useful to developers for debugging the application, not useful during operations"""
        if root_logger._log_level <= 10:
            root_logger.log(10, self._name, kw.pop('refs') if 'refs' in kw else [], format, *a, **kw)

    def inform(self, format, *a, **kw):
        """INFORMATIONAL: Normal operational messages - may be harvested for reporting, measuring throughput, etc - no action required"""
        if root_logger._log_level <= 20:
            root_logger.log(20, self._name, kw.pop('refs') if 'refs' in kw else [], format, *a, **kw)

    def warn(self, format, *a, **kw):
        """WARNING: Warning messages - not an error, but indication that an error will occur if action is not taken, e.g. file system 85% full - each item must be resolved within a given time"""
        if root_logger._log_level <= 30:
            root_logger.log(30, self._name, kw.pop('refs') if 'refs' in kw else [], format, *a, **kw)

    def error(self, format, *a, **kw):
        """ERROR: Non-urgent failures - these should be relayed to developers or admins; each item must be resolved within a given time"""
        if root_logger._log_level <= 40:
            root_logger.log(40, self._name, kw.pop('refs') if 'refs' in kw else [], format, *a, **kw)

    def crit(self, format, *a, **kw):
        """CRITICAL: Should be corrected immediately, but indicates failure in a primary system - fix CRITICAL problems before ALERT - example is loss of primary ISP connection"""
        if root_logger._log_level <= 50:
            root_logger.log(50, self._name, kw.pop('refs') if 'refs' in kw else [], format, *a, **kw)

class InstanceLogger():

    def __init__(self, name, instance, refs=None):
        self._name = name
        self._instance = instance
        self._refs = refs if refs else []

    def add_ref(self, name, instance, func):
        self._refs.append((name, instance, func))

    def debug(self, format, *a, **kw):
        """DEBUG: Info useful to developers for debugging the application, not useful during operations"""
        if root_logger._log_level <= 10:
            refs = self._refs[:]
            if 'refs' in kw:
                refs += kw.pop('refs')
            root_logger.log(10, self._name, refs, format, *a, **kw)

    def inform(self, format, *a, **kw):
        """INFORMATIONAL: Normal operational messages - may be harvested for reporting, measuring throughput, etc - no action required"""
        if root_logger._log_level <= 20:
            refs = self._refs[:]
            if 'refs' in kw:
                refs += kw.pop('refs')
            root_logger.log(20, self._name, refs, format, *a, **kw)

    def warn(self, format, *a, **kw):
        """WARNING: Warning messages - not an error, but indication that an error will occur if action is not taken, e.g. file system 85% full - each item must be resolved within a given time"""
        if root_logger._log_level <= 30:
            refs = self._refs[:]
            if 'refs' in kw:
                refs += kw.pop('refs')
            root_logger.log(30, self._name, refs, format, *a, **kw)

    def error(self, format, *a, **kw):
        """ERROR: Non-urgent failures - these should be relayed to developers or admins; each item must be resolved within a given time"""
        if root_logger._log_level <= 40:
            refs = self._refs[:]
            if 'refs' in kw:
                refs += kw.pop('refs')
            root_logger.log(40, self._name, refs, format, *a, **kw)

    def crit(self, format, *a, **kw):
        """CRITICAL: Should be corrected immediately, but indicates failure in a primary system, example is loss of primary ISP connection"""
        if root_logger._log_level <= 50:
            refs = self._refs[:]
            if 'refs' in kw:
                refs += kw.pop('refs')
            root_logger.log(50, self._name, refs, format, *a, **kw)
