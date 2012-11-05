
from handlers import BaseHandler, _logging2syslog
from loggers import RootLogger

root_logger = RootLogger()

import sys
import traceback

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
        # if we catched an error, do some trickery if it is a multiline message
        # or directly print the generated traceback from the failure object, if existing
        if a.get('isError'):
            message = a['message'] and a['message'][0]
            print_it = False
            if message and message.startswith('Traceback'):
                self._traceback = [message]
            elif self._traceback and (message and message.startswith(' ')):
                self._traceback.append(message)
            elif 'failure' in a:
                print_it = True
                failure_traceback = a['failure'].getTracebackObject()
                self._traceback = \
                    traceback.format_list(traceback.extract_tb(failure_traceback)) \
                    if failure_traceback else ['Unknown Error']
            else:
                print_it = True
                self._traceback.append(message)
            if print_it:
                if root_logger._log_level <= 40:
                    traceback_message = "\n".join(msg for msg in self._traceback)
                    root_logger.log(40, a.get('system', '-'), [], "%s", traceback_message, printed=1, unhandled=1)
                self._traceback = []
        # if there was a print statement, forward it on INFO
        elif root_logger._log_level <= 20:
            message = a['message'] and a['message'][0]
            root_logger.log(20, a.get('system', '-'), [], "%s", message, printed=1)
    
