# coding=utf-8

"""
    http://regebro.wordpress.com/2010/12/13/python-implementing-rich-comparison-the-correct-way/
"""


class ComparableMixin(object):
    """
    Adds comparison operators when mixed with a class.

    The class is required to implement a _cmpkey() method that returns an object that can be compared.
    """
    def _compare(self, other, method):
        try:
            #noinspection PyProtectedMember
            return method(self._cmpkey(), other._cmpkey())
        except (AttributeError, TypeError):
            # _cmpkey not implemented, or return different type,
            # so I can't compare with "other".
            return NotImplemented

    def _cmpkey(self):
        raise NotImplementedError

    def __lt__(self, other):
        return self._compare(other, lambda s, o: s < o)

    def __le__(self, other):
        return self._compare(other, lambda s, o: s <= o)

    def __eq__(self, other):
        return self._compare(other, lambda s, o: s == o)

    def __ge__(self, other):
        return self._compare(other, lambda s, o: s >= o)

    def __gt__(self, other):
        return self._compare(other, lambda s, o: s > o)

    def __ne__(self, other):
        return self._compare(other, lambda s, o: s != o)
