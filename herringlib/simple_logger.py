# coding=utf-8

"""
A simple logger that supports multiple output streams on a per level basis.
"""

__docformat__ = 'restructuredtext en'

import sys

__all__ = ('SimpleLogger', 'Logger', 'debug', 'info', 'warning', 'error', 'fatal')


class SimpleLogger(object):
    """A simple logger that supports multiple output streams on a per level basis."""

    def __init__(self, out_stream=sys.stdout, err_stream=sys.stderr):
        """Initialize"""
        self.current_component = None
        self.show_level = False
        self.log_outputter = {
            'debug': [],
            'info': [out_stream],
            'warning': [out_stream],
            'error': [err_stream],
            'fatal': [err_stream],
        }

    def set_verbose(self, verbose=True):
        """
        Set verbose mode.

        :param verbose: if verbose, then info messages are sent to stdout.
         :type verbose: bool
        """
        if verbose:
            self.log_outputter['info'] = [sys.stdout]
        else:
            self.log_outputter['info'] = []

    def set_debug(self, enable_debug=True):
        """
        Set debug logging mode.
    
        :param enable_debug: if debug, then debug messages are sent to stdout.
        :type enable_debug: bool
        """
        if enable_debug:
            self.log_outputter['debug'] = [sys.stdout]
            self.log_outputter['info'] = [sys.stdout]
        else:
            self.log_outputter['debug'] = []

    def set_component(self, component=None):
        """
        Set component label.

        :param component: the component label to insert into the message string.
        :type component: str
        """
        self.current_component = component

    def set_show_level(self, show_level=True):
        """
        Enable showing the logging level.
    
        :param show_level: if on, then include the log level of the message (DEBUG, INFO, ...) in the output.
        :type show_level: bool
        """
        self.show_level = show_level

    def _output(self, level, message):
        """
        Assemble the message and send it to the appropriate stream(s).

        :param level: the log level ('debug', 'info', 'warning', 'error', 'fatal')
        :type level: str
        :param message: the message to include in the output message.
        :type message: str
        """
        buf = []
        if self.show_level:
            buf.append("{level}:  ".format(level=level.upper()))
        if self.current_component:
            buf.append("[{component}]  ".format(component=str(self.current_component)))
        buf.append(str(message))
        buf.append("\n")
        line = ''.join(buf)
        for outputter in self.log_outputter[level]:
            if outputter:
                outputter.write(line)
                outputter.flush()

    def debug(self, message):
        """
        Debug message.
    
        :param message: the message to emit
        :type message: object that can be converted to a string using str()
        """
        self._output('debug', message)

    def info(self, message):
        """
        Info message.
    
        :param message: the message to emit
        :type message: object that can be converted to a string using str()
        """
        self._output('info', message)

    def warning(self, message):
        """
        Warning message.
    
        :param message: the message to emit
        :type message: object that can be converted to a string using str()
        """
        self._output('warning', message)

    def error(self, message):
        """
        Error message.
    
        :param message: the message to emit
        :type message: object that can be converted to a string using str()
        """
        self._output('error', message)

    def fatal(self, message):
        """
        Fatal message.
    
        :param message: the message to emit
        :type message: object that can be converted to a string using str()
        """
        self._output('fatal', message)
        exit(1)


Logger = SimpleLogger()

# pylint: disable=C0103
debug = Logger.debug
info = Logger.info
warning = Logger.warning
error = Logger.error
fatal = Logger.fatal
