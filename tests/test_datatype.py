# -*- coding: utf-8 -*-
# Zinc dumping and parsing module
# (C) 2016 VRT Systems
#
# vim: set ts=4 sts=4 et tw=78 sw=4 si:

# Assume unicode literals as per Python 3
from __future__ import unicode_literals
from .pint_enable import _enable_pint

import six
import hszinc
from copy import copy, deepcopy
import pytest

def check_singleton_deepcopy(S):
    orig_dict = {'some_value': S}
    copy_dict = deepcopy(orig_dict)
    assert copy_dict['some_value'] is S

def test_marker_deepcopy():
    check_singleton_deepcopy(hszinc.MARKER)

def test_remove_deepcopy():
    check_singleton_deepcopy(hszinc.REMOVE)

def check_singleton_copy(S):
    assert copy(S) is S

def test_marker_copy():
    check_singleton_copy(hszinc.MARKER)

def test_remove_copy():
    check_singleton_copy(hszinc.REMOVE)

def test_ref_notref_eq():
    r1 = hszinc.Ref(name='a.ref')
    r2 = 'not.a.ref'
    assert r1 is not r2
    assert not (r1 == r2)

def test_ref_notref_ne():
    r1 = hszinc.Ref(name='a.ref')
    r2 = 'not.a.ref'
    assert r1 is not r2
    assert r1 != r2

def test_ref_simple_eq():
    r1 = hszinc.Ref(name='a.ref')
    r2 = hszinc.Ref(name='a.ref')
    assert r1 is not r2
    assert r1 == r2

def test_ref_simple_neq_id():
    r1 = hszinc.Ref(name='a.ref')
    r2 = hszinc.Ref(name='another.ref')
    assert r1 is not r2
    assert r1 != r2

def test_ref_mixed_neq():
    r1 = hszinc.Ref(name='a.ref')
    r2 = hszinc.Ref(name='a.ref', value='display text')
    assert r1 is not r2
    assert r1 != r2

def test_ref_withdis_eq():
    r1 = hszinc.Ref(name='a.ref', value='display text')
    r2 = hszinc.Ref(name='a.ref', value='display text')
    assert r1 is not r2
    assert r1 == r2

def test_ref_withdis_neq_id():
    r1 = hszinc.Ref(name='a.ref', value='display text')
    r2 = hszinc.Ref(name='another.ref', value='display text')
    assert r1 is not r2
    assert r1 != r2

def test_ref_withdis_neq_dis():
    r1 = hszinc.Ref(name='a.ref', value='display text')
    r2 = hszinc.Ref(name='a.ref', value='different display text')
    assert r1 is not r2
    assert r1 != r2

@pytest.mark.parametrize("float_values", [123.45, -123.45])
@pytest.mark.parametrize("int_values", [123, -123])
def test_qty_unary_ops(float_values, int_values):
    # How to run the test: check the result
    # applied to the Quantity object matches what
    # would be returned for the same operation applied
    # to the raw value.
    float_values = float_values
    int_values = int_values
    def _check_qty_op(pint_en, fn, *vals):
        _enable_pint(pint_en)
        for v in vals:
            q = hszinc.Quantity(v)
            return fn(q) == fn(q.value)

    # Try this both without, and with, pint enabled
    for pint_en in (False, True):
        # These work for floats
        for fn in ( lambda v : int(v),
                    lambda v : complex(v),
                    lambda v : float(v),
                    lambda v : -v,
                    lambda v : +v,
                    lambda v : abs(v)):
            #yield _check_qty_op, pint_en, fn, 123.45, -123.45
            assert _check_qty_op(pint_en, fn, float_values)

        # These work for integers
        for fn in ( lambda v : oct(v),
                    lambda v : hex(v),
                    lambda v : v.__index__(),
                    lambda v : int(v),
                    lambda v : complex(v),
                    lambda v : float(v),
                    lambda v : -v,
                    lambda v : +v,
                    lambda v : abs(v),
                    lambda v : ~v):
            #yield _check_qty_op, pint_en, fn, 123, -123
            assert _check_qty_op(pint_en, fn, int_values)

        # This only works with Python 2.
        if six.PY2:
            #yield _check_qty_op, pint_en, lambda v : long(v), 123.45, -123.45
            assert _check_qty_op(pint_en, lambda v : long(v), float_values)

@pytest.mark.parametrize("pint_en", [True, False])
@pytest.mark.parametrize("values", [123.45, -123.45, 12345, -12345, (50,'Hz')])
def test_qty_hash(pint_en, values):
    def _check_qty_hash(pint_en):
        # Test that independent copies hash to the same value
        def _check_hash(val, unit=None):
            a = hszinc.Quantity(val, unit=unit)
            b = hszinc.Quantity(val, unit=unit)
            return (a is not b) and (hash(a) == hash(b))

        _enable_pint(pint_en)
        return _check_hash(values)

    assert _check_qty_hash(pint_en)

@pytest.mark.parametrize("pint_en", [True, False])
@pytest.mark.parametrize("floats", [1.12, 2.23, -4.56, 141.2, -399.5])
@pytest.mark.parametrize("ints", [1, 2, -4, 141, -399, 0x10, 0xff, 0x55])
def test_qty_binary_ops(pint_en, floats, ints):
    def _check_qty_op(pint_en, fn, a, b):
        _enable_pint(pint_en)
        qa = hszinc.Quantity(a)
        qb = hszinc.Quantity(b)

        # Reference value
        ref = fn(a, b)

        test1 = fn(qa, qb) == ref
        test2 = fn(qa, b) == ref
        test3 = fn(a, qb) == ref
        return test1 and test2 and test3

    for fn in ( lambda a, b : a + b,
                lambda a, b : a - b,
                lambda a, b : a * b,
                lambda a, b : a / b,
                lambda a, b : a // b,
                lambda a, b : a % b,
                lambda a, b : divmod(a, b),
                lambda a, b : a < b,
                lambda a, b : a <= b,
                lambda a, b : a == b,
                lambda a, b : a != b,
                lambda a, b : a >= b,
                lambda a, b : a > b):
        assert _check_qty_op(pint_en, fn, floats, floats)

        # Exponentiation, we can't use all the values above
        # as some go out of range.
        #small_floats = tuple(filter(lambda f : abs(f) < 10, floats))
        #for a in small_floats:
        #    for b in small_floats:
        #        if a == b:
        #            continue##
#
#                # Python2 won't allow raising negative numbers
#                # to a fractional power
#                if a < 0:
#                    continue#
#
#                yield _check_qty_op, pint_en, lambda a, b: a ** b, a, b

        # Try some integer values
    for fn in ( lambda a, b : a + b,
                lambda a, b : a - b,
                lambda a, b : a * b,
                lambda a, b : a / b,
                lambda a, b : a // b,
                lambda a, b : a % b,
                lambda a, b : divmod(a, b),
                lambda a, b : a & b,
                lambda a, b : a ^ b,
                lambda a, b : a | b,
                lambda a, b : a < b,
                lambda a, b : a <= b,
                lambda a, b : a == b,
                lambda a, b : a != b,
                lambda a, b : a >= b,
                lambda a, b : a > b):
        assert _check_qty_op(pint_en, fn, ints, ints)

        if ints >= 0:
            for fn in ( lambda a, b : a << b,
                        lambda a, b : a >> b):
                assert _check_qty_op(pint_en, fn, ints, ints)

        # Exponentiation, we can't use all the values above
        # as some go out of range.
        #small_ints = tuple(filter(lambda f : abs(f) < 10, ints))
        #for a in small_ints:
        #    for b in small_ints:
        #        if a == b:
        #            continue
#
#                yield _check_qty_op, pint_en, lambda a, b: a ** b, a, b

@pytest.mark.parametrize("pint_en", [True, False])
@pytest.mark.parametrize("values", [hszinc.Quantity(-3),hszinc.Quantity(432),hszinc.Quantity(4, unit='A'),hszinc.Quantity(10, unit='A'),hszinc.Quantity(12, unit='V')])
def test_qty_cmp(pint_en, values):
    def _check_qty_cmp(pint_en):
        if 'cmp' not in set(locals().keys()):
            def cmp(a, b):
                return a.__cmp__(b)

        _enable_pint(pint_en)

        a = hszinc.Quantity(-3)
        b = hszinc.Quantity(432)
        c = hszinc.Quantity(4, unit='A')
        d = hszinc.Quantity(10, unit='A')
        e = hszinc.Quantity(12, unit='V')

        assert cmp(a, b) < 0
        assert cmp(b, a) > 0
        assert cmp(a, hszinc.Quantity(-3)) == 0
        assert cmp(c, d) < 0
        assert cmp(d, c) > 0
        assert cmp(c, hszinc.Quantity(4, unit='A')) == 0

        try:
            cmp(c, e)
        except TypeError as ex:
            assert str(ex) == 'Quantity units differ: A vs V'

    _check_qty_cmp(pint_en)

class MyCoordinate(object):
    """
    A dummy class that can compare itself to a Coordinate from hszinc.
    """
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def __eq__(self, other):
        if isinstance(other, hszinc.Coordinate):
            return (self.lat == other.latitude)\
                    and (self.lng == other.longitude)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, hszinc.Coordinate):
            return (self.lat != other.latitude)\
                    and (self.lng != other.longitude)
        return NotImplemented


def test_coord_eq():
    assert hszinc.Coordinate(latitude=33.77, longitude=-77.45) \
            == hszinc.Coordinate(latitude=33.77, longitude=-77.45)

def test_coord_eq_notcoord():
    assert not (hszinc.Coordinate(latitude=33.77, longitude=-77.45) \
            == (33.77, -77.45))

def test_coord_eq_mycoord():
    hsc = hszinc.Coordinate(latitude=33.77, longitude=-77.45)
    mc = MyCoordinate(33.77, -77.45)
    assert hsc == mc
    assert mc == hsc

def test_coord_ne():
    assert hszinc.Coordinate(latitude=-33.77, longitude=77.45) \
            != hszinc.Coordinate(latitude=33.77, longitude=-77.45)

def test_coord_ne_notcoord():
    assert (hszinc.Coordinate(latitude=33.77, longitude=-77.45) \
            != (33.77, -77.45))

def test_coord_ne_mycoord():
    hsc = hszinc.Coordinate(latitude=33.77, longitude=-77.45)
    mc = MyCoordinate(-33.77, 77.45)
    assert hsc != mc
    assert mc != hsc
