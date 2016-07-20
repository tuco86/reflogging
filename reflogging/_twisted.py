
from .handlers import BaseHandler, _logging2syslog
from .loggers import RootLogger

root_logger = RootLogger()

import sys

orig_stdout = sys.stdout


class TwistedHandler(BaseHandler):

    def __init__(self, log_publisher):
        BaseHandler.__init__(self)
        self._log_publisher = log_publisher

    def record(self, severity, name, message, refs, **kw):
        for message in message.split('\n'):
            self._log_publisher.msg(
                '[' + "".join(["<%s %s>" % (n, v) for n, v in refs]) + '] ' + message,
                system=name,
                syslogPriority=_logging2syslog[severity]
            )


class RefloggingObserver:

    def __init__(self):
        self._traceback = []

    def __call__(self, a):
        isError = a.get('isError')
        printed = a.get('printed')
        failure = a.get('failure')

        if isError:
            if failure:
                root_logger.log(40, a.get('system', '-'), [], failure.getTraceback()[:-1], printed=1, unhandled=1)
                return
            if printed:
                if a['message'][0].startswith('Traceback'):
                    self._traceback.append(a)
                    return
                if self._traceback and not a['message'][0].startswith(' '):
                    self._traceback.append(a)
                    if root_logger._log_level <= 40:
                        root_logger.log(40, a.get('system', '-'), [], "\n".join([trace['message'][0] for trace in self._traceback]), printed=1, unhandled=1)
                    self._traceback = []
                    return
                if self._traceback:
                    self._traceback.append(a)
                    return
        if root_logger._log_level <= 20:
            root_logger.log(20, a.get('system', '-'), [], a['message'][0], printed=1)
