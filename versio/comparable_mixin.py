# coding=utf-8
"""
    http://regebro.wordpress.com/2010/12/13/python-implementing-rich-comparison-the-correct-way/
"""

__docformat__ = 'restructuredtext en'


def _cmp(a, b):
    if a < b:
        return -1
    elif a > b:
        return 1
    else:
        return 0


class ComparableMixin(object):
    """
    Mix in this class and implement a **_cmpkey()** method to make an object comparable.
    """
    def _compare(self, other, method):
        """
        Compare an object with this object using the given comparison method.

        :param other: object ot compare with
        :type other: ComparableMixin
        :param method: a comparison method
        :type method: lambda
        :return: asserted if comparison is true
        :rtype: bool
        :raises: NotImplemented
        """
        try:
            return method(self._cmpkey(), other._cmpkey())
        except (AttributeError, TypeError):
            # _cmpkey not implemented, or return different type,
            # so I can't compare with "other".
            return NotImplemented

    def _cmpkey(self):
        """
        The comparison key must be implemented by the child class and used by the comparison operators.
        """
        raise NotImplementedError

    def __lt__(self, other):
        """
        less than

        :param other: the instance to compare to
        :type other: ComparableMixin
        """
        return self._compare(other, lambda s, o: _cmp(s, o) < 0)

    def __le__(self, other):
        """
        less than or equal

        :param other: the instance to compare to
        :type other: ComparableMixin
        """
        return self._compare(other, lambda s, o: _cmp(s, o) <= 0)

    def __eq__(self, other):
        """
        equal

        :param other: the instance to compare to
        :type other: ComparableMixin
        """
        return self._compare(other, lambda s, o: _cmp(s, o) == 0)

    def __ge__(self, other):
        """
        greater than or equal

        :param other: the instance to compare to
        :type other: ComparableMixin
        """
        return self._compare(other, lambda s, o: _cmp(s, o) >= 0)

    def __gt__(self, other):
        """
        greater than

        :param other: the instance to compare to
        :type other: ComparableMixin
        """
        return self._compare(other, lambda s, o: _cmp(s, o) > 0)

    def __ne__(self, other):
        """
        not equal

        :param other: the instance to compare to
        :type other: ComparableMixin
        """
        return self._compare(other, lambda s, o: _cmp(s, o) != 0)
