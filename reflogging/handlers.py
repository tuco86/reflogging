
import atexit
import time
import socket
import signal
from multiprocessing import Process, Pipe
from zlib import compress
from cjson import encode
from reflogging import root_logger
import os
import syslog

_logging2syslog = {10: 7, 20: 6, 30: 4, 40: 3, 50: 2}
_logging2char = {10: 'D', 20: 'I', 30: 'W', 40: 'E', 50: 'C'}

class BaseHandler():

    def __init__(self):
        self._log_level = 10

    def set_level(self, level):
        assert level in (10, 20, 30, 40, 50),\
            'Level(%s) has to be in (10, 20, 30, 40, 50)' % (level,)
        self._log_level = level

    def record(self, *a, **kw):
        raise NotImplementedError

from sys import stdout

class GELFHandler(BaseHandler):

    def __init__(self, host, port=12201):
        BaseHandler.__init__(self)
        self.deactivated = False
        self._record_pipe, process_pipe = Pipe(True)
        self._process = Process(target=self._run, args=(process_pipe, host, port), name='GELFHandler')
        self._process.daemonhtop = True
        self._process.start()
        atexit.register(self._record_pipe.send, -1)

    def _run(self, pipe, host, port):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _socket.connect((host, port))
        _hostname = socket.gethostname()
        for time, severity, name, message, kw in iter(pipe.recv, -1):
            fields = {
                'version': '1.0',
                'host': _hostname,
                'short_message': message.split('\n', 1)[0],
                'full_message': message,
                'timestamp': time,
                'level': _logging2syslog[severity],
                'facility': name
            }
            for k, v in kw.iteritems():
                fields['_'+k] = v
            raw = compress(encode(fields))
            try:
                _socket.send(raw)
            except socket.error, e:
                print >> stdout, 'socket errror:', str(e)

    def record(self, severity, name, refs, format, *a, **kw):
        if self.deactivated:
            return
        for n, v in refs:
            kw[n] = v
        try:
            self._record_pipe.send((time.time(), severity, name, format % a if a else format, kw))
        except IOError, e:
            self._record_pipe.close()
            self.deactivated = True
            root_logger.log(50, 'reflogging.handlers.GELFHandler', [], 'GELFHandler\'s record_pipe went down: %s' % (str(e),))



class StreamHandler(BaseHandler):

    def __init__(self, stream):
        BaseHandler.__init__(self)
        self._stream = stream

    def record(self, severity, name, refs, format, *a, **kw):
        message = format % a if a else format
        self._stream.write("%s %s %s [%s] %s\n" % (
            time.strftime("%H:%M:%S"),
            _logging2char[severity],
            name,
            "".join(["<%s %s>" % (n, v) for n, v in refs]),
            message.replace('\n', '\n    ')
        ))
        self._stream.flush()

class ColorStreamHandler(BaseHandler):

    def __init__(self, stream):
        BaseHandler.__init__(self)
        self._stream = stream

    def record(self, severity, name, refs, format, *a, **kw):
        format = format \
            .replace("%s", "\033[33m%s\033[0m") \
            .replace("%d", "\033[31m%d\033[0m") \
            .replace("%f", "\033[31m%f\033[0m")
        message = format % a if a else format
        self._stream.write("\033[30m%s %s\033[0m\033[30m %s [%s]\033[0m %s\n" % (
            time.strftime("%H:%M:%S"),
            ['\033[36m', '\033[32m', '\033[33m', '\033[31m', '\033[0;30m\033[41m'][severity/10-1] + _logging2char[severity],
            name,
            "".join(["<\033[33m%s\033[0m \033[31m%s\033[30m>" % (n, v) for n, v in refs if v]),
            ('\\\n    ' if '\n' in message else '') + message.replace('\n', '\n    ')
        ))
        self._stream.flush()

class SyslogHandler(BaseHandler):

    def __init__(self, ident, logoption, facility=syslog.LOG_USER):
        syslog.openlog(ident, logoption, facility)


    def record(self, severity, name, refs, format, *a, **kw):
        message = format % a if a else format
        refstring = "".join(["<%s %s>" % (n, v) for n, v in refs])
        for line in message.split('\n'):
            syslog.syslog(
                _logging2syslog[severity],
                "%s [%s] %s" % (
                    name,
                    refstring,
                    line
                )
            )
