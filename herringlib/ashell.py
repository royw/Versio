# coding=utf-8

"""
This is the abstract base class for the LocalShell and RemoteShell objects.  AShell is responsible for defining
their common public interface.
"""
import os
import sys

__docformat__ = 'restructuredtext en'
__author__ = 'wrighroy'

CR = '\r'
LF = '\n'
BS = '\b'
FF = '\f'
MOVEMENT = r'(\r\n|[\r\n\b\f])'


class AShell(object):
    """
    The __enter__() and __exit__() methods provide support for the **with** syntax.  Usage::

        with LocalShell() as local:
            local.run(...)
    """
    def __init__(self, is_remote, verbose=False):
        self.verbose = verbose
        self.prefix = None
        self.postfix = None
        self.logfile = None
        self.is_remote = is_remote

    def __enter__(self):
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.logout()

    def expand_args(self, cmd_args, prefix=None, postfix=None):
        """adds the prefix and postfix lists to the given cmd_args list."""
        args = list(cmd_args)

        if prefix:
            args = prefix + args
        elif self.prefix:
            args = self.prefix + args

        if postfix:
            args = args + postfix
        elif self.postfix:
            args = args + self.postfix

        return args

    def display(self, line, out_stream=sys.stdout, verbose=False):
        """Simple display that writes the given line to out_stream if verbose is enabled"""
        if self.verbose or verbose:
            out_stream.write(str(line))
            out_stream.flush()
            if self.logfile:
                with open(self.logfile, 'a') as log_stream:
                    log_stream.write(str(line))
                    log_stream.flush()

    def run(self, cmd_args, out_stream=sys.stdout, env=None, verbose=True,
            prefix=None, postfix=None, accept_defaults=False, pattern_response=None, timeout=120):
        raise NotImplementedError

    def system(self, cmd_line, out_stream=sys.stdout, prefix=None, postfix=None, verbose=True):
        """
        simple system runner with optional verbose echo of command and results.

        Execute the given command line and wait for completion.

        :param out_stream:
        :param prefix:
        :param postfix:
        :param cmd_line: command line to execute
        :type cmd_line: str
        :param verbose: asserted to echo command and results
        :type verbose: bool
        """
        self.display("system(%s)\n\n" % cmd_line, out_stream=out_stream, verbose=verbose)
        command_line = ' '.join(self.expand_args([cmd_line], prefix=prefix, postfix=postfix))
        # self.display(command_line + '\n', out_stream=out_stream, verbose=verbose)
        result = self._system(command_line)
        self.display(str(result) + '\n', out_stream=out_stream, verbose=verbose)
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
        self.display("script(%s)\n\n" % cmdline, out_stream=sys.stdout, verbose=verbose)
        return self.run(['script', '-q', '-e', '-f', '-c', cmdline], verbose=verbose, env=env)

    def _system(self, command_line):
        raise NotImplementedError

    def logout(self):
        pass

    def mysql(self, user, password, sql=None):
        if sql:
            pid = os.getpid()
            config = ".my.cnf.{pid}".format(pid=pid)
            command = ".mysql.{pid}".format(pid=pid)

            def do_query(sql_query):
                # note, self is from the outer scope
                self.system('echo "{sql}" >{command}'.format(sql=sql_query, command=command))
                self.system('mysql --defaults-file={config} <{command}'.format(config=config, command=command))
                self.system('rm -f {command}'.format(command=command))

            try:
                self.system('echo "# mysql_secure_installation config file" >{config}'.format(config=config))
                self.system('echo "[mysql]" >>{config}'.format(config=config))
                self.system('echo "user={user}" >>{config}'.format(user=user, config=config))
                self.system('echo "password={password}" >>{config}'.format(password=password, config=config))

                self.system('cat {config}'.format(config=config))

                for query in map(str.strip, sql.format(user=user, password=password).split("\n")):
                    do_query(query)
            finally:
                self.system('rm -f {config}'.format(config=config))
