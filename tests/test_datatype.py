# -*- coding: utf-8 -*-
# Zinc dumping and parsing module
# (C) 2016 VRT Systems
#
# vim: set ts=4 sts=4 et tw=78 sw=4 si:

# Assume unicode literals as per Python 3
from __future__ import unicode_literals

import binascii
import random
from copy import copy, deepcopy

import six
import pytest

import hszinc
from hszinc.datatypes import XStr, Uri, Bin, MARKER, NA, REMOVE
from hszinc.pintutil import to_haystack, to_pint
from .pint_enable import _enable_pint

if not six.PY2:  # pragma: no cover
    # We don't use this alias, but flake8 will moan if we don't define it!
    long = int


def check_singleton_deepcopy(S):
    orig_dict = {'some_value': S}
    copy_dict = deepcopy(orig_dict)
    assert copy_dict['some_value'] is S


def test_marker_deepcopy():
    check_singleton_deepcopy(hszinc.MARKER)


def test_marker_hash():
    assert hash(hszinc.MARKER) == hash(hszinc.MARKER.__class__)


def test_remove_deepcopy():
    check_singleton_deepcopy(hszinc.REMOVE)


def test_remove_hash():
    assert hash(hszinc.REMOVE) == hash(hszinc.REMOVE.__class__)


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


def test_ref_hash():
    assert hash(hszinc.Ref(name='a.ref', value='display text')) == \
           hash('a.ref') ^ hash('display text') ^ hash(True)


def test_ref_std_method():
    if six.PY2:
        assert str(hszinc.Ref(name='a.ref', value='display text')) == '@a.ref u\'display text\''
    else:
        assert str(hszinc.Ref(name='a.ref', value='display text')) == '@a.ref \'display text\''

@pytest.mark.parametrize("pint_en,fn,value", [
    (pint_en, fn, value) \
            for pint_en in (False, True) \
            for fn in (
                lambda v: oct(v),
                lambda v: hex(v),
                lambda v: v.__index__(),
                lambda v: int(v),
                lambda v: long(v),
                lambda v: complex(v),
                lambda v: float(v),
                lambda v: -v,
                lambda v: +v,
                lambda v: abs(v),
                lambda v: ~v
            )
            for value in (123, -123)
])
def test_qty_unary_int_op(pint_en, fn, value):
    _enable_pint(pint_en)
    q = hszinc.Quantity(value)
    assert fn(q) == fn(q.value)

@pytest.mark.parametrize("pint_en,fn,value", [
    (pint_en, fn, value) \
            for pint_en in (False, True) \
            for fn in (
                lambda v: int(v),
                lambda v: complex(v),
                lambda v: float(v),
                lambda v: -v,
                lambda v: +v,
                lambda v: abs(v)
            ) \
            for value in (123.45, -123.45)
])
def test_qty_unary_float_op(pint_en, fn, value):
    _enable_pint(pint_en)
    q = hszinc.Quantity(value)
    assert fn(q) == fn(q.value)


@pytest.mark.parametrize("pint_en,value,unit", [
    (pint_en, value, unit)
    for pint_en in (False, True)
    for (value, unit) in (
        (123.45, None),
        (-123.45, None),
        (12345, None),
        (-12345, None),
        (50, 'Hz')
    )
])
def test_qty_hash(pint_en, value, unit):
    _enable_pint(pint_en)
    a = hszinc.Quantity(value, unit=unit)
    b = hszinc.Quantity(value, unit=unit)

    assert a is not b
    assert hash(a) == hash(b)

FLOATS = (1.12, 2.23, -4.56, 141.2, -399.5)
@pytest.mark.parametrize("pint_en,fn,a,b", [
    (pint_en, fn, a, b) \
            for pint_en in (False, True) \
            for fn in (lambda a, b: a + b,
                lambda a, b: a - b,
                lambda a, b: a * b,
                lambda a, b: a / b,
                lambda a, b: a // b,
                lambda a, b: a % b,
                lambda a, b: divmod(a, b),
                lambda a, b: a < b,
                lambda a, b: a <= b,
                lambda a, b: a == b,
                lambda a, b: a != b,
                lambda a, b: a >= b,
                lambda a, b: a > b) \
            for (a, b) in [
                # Cross product of all FLOATS elements, except those that
                # match
                (a, b) for a in FLOATS for b in FLOATS if a != b
            ]
])
def test_qty_float_binary_op(pint_en, fn, a, b):
    _enable_pint(pint_en)
    qa = hszinc.Quantity(a)
    qb = hszinc.Quantity(b)

    # Reference value
    ref = fn(a, b)

    assert fn(qa, qb) == ref
    assert fn(qa, b) == ref
    assert fn(a, qb) == ref

# Exponentiation, we can't use all the values above
# as some go out of dates_range.
SMALL_FLOATS = tuple(filter(lambda f: abs(f) < 10, FLOATS))
@pytest.mark.parametrize("pint_en,a,b", [
    (pint_en, a, b) \
            for pint_en in (False, True) \
            for (a, b) in [
                # Cross product of all SMALL_FLOATS elements, except those
                # that match.  Python 2.7 can't raise negative numbers to
                # fractional exponents.
                (a, b) for a in SMALL_FLOATS for b in SMALL_FLOATS \
                        if (a != b) and ((not six.PY2) or (a > 0))
            ]
])
def test_qty_float_exp(pint_en, a, b):
    _enable_pint(pint_en)
    qa = hszinc.Quantity(a)
    qb = hszinc.Quantity(b)

    # Reference value
    ref = a ** b

    assert qa ** qb == ref
    assert qa ** b == ref
    assert a ** qb == ref

INTS = (1, 2, -4, 141, -399, 0x10, 0xff, 0x55)
@pytest.mark.parametrize("pint_en,fn,a,b", [
    (pint_en, fn, a, b) \
            for pint_en in (False, True) \
            for fn in (
                lambda a, b: a + b,
                lambda a, b: a - b,
                lambda a, b: a * b,
                lambda a, b: a / b,
                lambda a, b: a // b,
                lambda a, b: a % b,
                lambda a, b: divmod(a, b),
                lambda a, b: a & b,
                lambda a, b: a ^ b,
                lambda a, b: a | b,
                lambda a, b: a < b,
                lambda a, b: a <= b,
                lambda a, b: a == b,
                lambda a, b: a != b,
                lambda a, b: a >= b,
                lambda a, b: a > b,
            ) \
            for (a, b) in [
                # Cross product of all INTS elements, except those that
                # match
                (a, b) for a in INTS for b in INTS if a != b
            ]
])
def test_qty_int_binary_op(pint_en, fn, a, b):
    _enable_pint(pint_en)
    qa = hszinc.Quantity(a)
    qb = hszinc.Quantity(b)

    # Reference value
    ref = fn(a, b)

    assert fn(qa, qb) == ref
    assert fn(qa, b) == ref
    assert fn(a, qb) == ref

POS_INTS = (1, 2, 141, 0x10, 0xff, 0x55)
@pytest.mark.parametrize("pint_en,fn,a,b", [
    (pint_en, fn, a, b) \
            for pint_en in (False, True) \
            for fn in (
                lambda a, b: a << b,
                lambda a, b: a >> b,
            ) \
            for (a, b) in [
                # Cross product of all POS_INTS elements, except those that
                # match
                (a, b) for a in POS_INTS for b in POS_INTS if a != b
            ]
])
def test_qty_int_shift_op(pint_en, fn, a, b):
    _enable_pint(pint_en)
    qa = hszinc.Quantity(a)
    qb = hszinc.Quantity(b)

    # Reference value
    ref = fn(a, b)

    assert fn(qa, qb) == ref
    assert fn(qa, b) == ref
    assert fn(a, qb) == ref


@pytest.mark.parametrize("pint_en", [(False,), (True,)])
def test_qty_cmp(pint_en):
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


@pytest.mark.parametrize("pint_en", [(False,), (True,)])
def test_qty_std_method(pint_en):
    r = repr(hszinc.Quantity(4, unit='A'))
    if six.PY2:
        assert (r == 'BasicQuantity(4, u\'A\')') or (r == 'PintQuantity(4, u\'A\')')
    else:
        assert (r == 'BasicQuantity(4, \'A\')') or (r == 'PintQuantity(4, \'A\')')
    assert str(hszinc.Quantity(4, unit='A')) == '4 A'


class MyCoordinate(object):
    """
    A dummy class that can compare itself to a Coordinate from hszinc.
    """

    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def __eq__(self, other):
        if isinstance(other, hszinc.Coordinate):
            return (self.lat == other.latitude) \
                   and (self.lng == other.longitude)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, hszinc.Coordinate):
            return (self.lat != other.latitude) \
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


def test_coord_hash():
    assert hash(hszinc.Coordinate(latitude=33.77, longitude=-77.45)) == \
           hash(33.77) ^ hash(-77.45)


def test_coord_default_method():
    coord = hszinc.Coordinate(latitude=33.77, longitude=-77.45)
    ref_str = u'33.770000° lat -77.450000° long'
    if six.PY2:
        ref_str = ref_str.encode('utf-8')

    assert repr(coord) == 'Coordinate(33.77, -77.45)'
    assert str(coord) == ref_str


def test_xstr_hex():
    assert XStr("hex", "deadbeef").data == b'\xde\xad\xbe\xef'
    barray = bytearray(random.getrandbits(8) for _ in range(10))
    assert barray == hszinc.XStr("hex", binascii.hexlify(barray).decode("ascii")).data


def test_xstr_other():
    assert (XStr("other", "hello word").data == "hello word")
    barray = bytearray(random.getrandbits(8) for _ in range(10))
    assert barray == hszinc.XStr("other", barray).data


def test_xstr_b64():
    assert XStr("b64", '3q2+7w==').data == b'\xde\xad\xbe\xef'
    barray = bytearray(random.getrandbits(8) for _ in range(10))
    assert barray == hszinc.XStr("b64", binascii.b2a_base64(barray)).data


def test_xstr_equal():
    assert XStr("hex", "deadbeef") == XStr("b64", '3q2+7w==')


def test_uri():
    uri = Uri("abc")
    assert uri == Uri("abc")
    if six.PY2:
        assert repr(uri) == 'Uri(u\'abc\')'
    else:
        assert repr(uri) == 'Uri(\'abc\')'
    assert str(uri) == 'abc'


def test_bin():
    bin = Bin("text/plain")
    if six.PY2:
        assert repr(bin) == 'Bin(u\'text/plain\')'
    else:
        assert repr(bin) == 'Bin(\'text/plain\')'
    assert str(bin) == 'text/plain'


def test_marker():
    assert repr(MARKER) == 'MARKER'


def test_na():
    assert repr(NA) == 'NA'


def test_remove():
    assert repr(REMOVE) == 'REMOVE'


def test_to_haystack():
    assert to_haystack('/h') == u''
    assert to_haystack(u'foot ** 3') == u'cubic_foot'
    assert to_haystack(u'deg') == u'\N{DEGREE SIGN}'

def test_to_pint():
    assert to_pint(u'\N{DEGREE SIGN}') == 'deg'
    assert to_pint('cubic_foot') == u'cubic foot'
