# coding=utf-8

"""
Run external scripts and programs.
"""

__docformat__ = 'restructuredtext en'

import os
import fcntl
import sys
import subprocess
from simple_logger import info
from graceful_interrupt_handler import GracefulInterruptHandler

__all__ = ('Runner', 'run', 'system', 'script')


class Runner(object):
    def __init__(self):
        self.verbose = False

    def _non_block_read(self, output):
        fd = output.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        #noinspection PyBroadException
        try:
            return output.read()
        except:
            return ''

    def run(self, cmd_args, env=None, verbose=True, prefix=None):
        """
        Down and dirty shell runner.  Yeah, I know, not pretty.

        :param cmd_args: list of command arguments
        :type cmd_args: list
        :param env: the environment variables for the command to use.
        :type env: dict
        :param verbose: if verbose, then echo the command and it's output to stdout.
        :type verbose: bool
        :param prefix: list of command arguments to prepend to the command line
        :type prefix: list
        """
        if self.verbose or verbose:
            sys.stdout.write(' '.join(cmd_args))
            sys.stdout.write('\n')
            sys.stdout.flush()
        lines = []

        args = cmd_args
        if prefix:
            args = prefix + cmd_args

        for line in self.run_process(args, env=env, verbose=verbose):
            if self.verbose or verbose:
                sys.stdout.write(line)
                sys.stdout.flush()
            lines.append(line)

        return "".join(lines)

    def run_process(self, exe, env=None, verbose=True):
        """
        Run the process yield for each output line from the process.

        :param exe: command line components
        :type exe: list
        :param env: environment
        :type env: dict
        :param verbose: outputs the method call if True
        :type verbose: bool
        """
        if self.verbose or verbose:
            sys.stdout.write("runProcess(%s, %s)\n" % (exe, env))
            sys.stdout.flush()
        sub_env = os.environ.copy()
        if env:
            for key, value in env.iteritems():
                sub_env[key] = value

        with GracefulInterruptHandler() as handler:
            process = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       env=sub_env)
            while process.poll() is None:   # returns None while subprocess is running
                if handler.interrupted:
                    process.kill()
                while True:
                    line = self._non_block_read(process.stdout)
                    if not line:
                        break
                    yield line

    def system(self, cmd_line, verbose=True):
        """
        simple system runner with optional verbose echo of command and results.

        Execute the given command line and wait for completion.

        :param cmd_line: command line to execute
        :type cmd_line: str
        :param verbose: asserted to echo command and results
        :type verbose: bool
        """
        if verbose:
            info(cmd_line)
        result = os.popen(cmd_line).read()
        if verbose:
            info(result)
        return result

    def script(self, cmdline, verbose=False, env=None):
        """
        Simple runner using the *script* utility to preserve color output by letting the
        command being ran think it is running on a console instead of a tty.

        See: man script

        :param cmdline: command line to run
        :type cmdline: str
        :param verbose: if verbose, then echo the command and it's output to stdout.
        :type verbose: bool
        :param env: environment variables or None
        :type env: dict
        :return: the output of the command line
        :rtype: str
        """
        self.run(['script', '-q', '-e', '-f', '-c', cmdline], verbose=verbose, env=env)

run = Runner().run
system = Runner().system
script = Runner().script
