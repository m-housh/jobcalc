#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jobcalc.exceptions import JobCalcError, InvalidEnvString, \
    EnvDictNotFound, NotCallableError


def test_JobCalcError():
    exc = JobCalcError('some message')
    assert str(exc) == 'JobCalcError: some message'
    assert repr(exc) == 'JobCalcError: some message'

    exc2 = JobCalcError()
    assert str(exc2) == 'JobCalcError'


def test_InvalidEnvString():
    exc = InvalidEnvString('a string')
    assert isinstance(exc, JobCalcError)
    assert isinstance(exc, TypeError)
    assert str(exc) == 'InvalidEnvString: a string'

    # checking that this can also be caught by a TypeError
    # try block
    try:
        raise exc
    except TypeError as err:
        assert isinstance(err, JobCalcError)


def test_EnvDictNotFound():
    exc = EnvDictNotFound('SOMETHING')
    assert isinstance(exc, JobCalcError)
    assert str(exc) == 'EnvDictNotFound: SOMETHING'


def test_NotCallableError():
    exc = NotCallableError(object())
    assert isinstance(exc, JobCalcError)
    assert isinstance(exc, TypeError)
    assert str(exc) == 'NotCallableError: object'
