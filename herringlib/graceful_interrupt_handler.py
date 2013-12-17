# coding=utf-8

"""
Graceful Interrupt Handler as a context manager.

Can be nested.

From:
http://stackoverflow.com/a/10972804
https://gist.github.com/nonZero/2907502
"""

__docformat__ = 'restructuredtext en'

import signal


class GracefulInterruptHandler(object):
    """
    Example Usage::

        with GracefulInterruptHandler() as h1:
            while True:
                print "(1)..."
                time.sleep(1)
                with GracefulInterruptHandler() as h2:
                    while True:
                        print "\t(2)..."
                        time.sleep(1)
                        if h2.interrupted:
                            print "\t(2) interrupted!"
                            time.sleep(2)
                            break
                if h1.interrupted:
                    print "(1) interrupted!"
                    time.sleep(2)
                    break
    """

    def __init__(self, sig=signal.SIGINT):
        self.sig = sig
        self.interrupted = False
        self.released = False
        self.original_handler = None

    def __enter__(self):

        self.interrupted = False
        self.released = False

        self.original_handler = signal.getsignal(self.sig)

        #noinspection PyUnusedLocal
        def handler(signum, frame):
            """signal that an interrupt has occurred."""
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)

        return self

    #noinspection PyUnusedLocal,PyShadowingBuiltins
    def __exit__(self, type, value, tb):
        self.release()

    def release(self):
        """release the signal handler"""
        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)

        self.released = True

        return True
