# -*- coding: utf-8 -*-

from typing import Any


class JobCalcError(Exception):
    """Base exception used by the app.  All custom exceptions should inherit
    from this class.
    """

    def __init__(self, msg: str=None) -> None:
        self.msg = msg

    def __str__(self) -> str:
        name = self.__class__.__name__

        if self.msg is not None:
            return '{}: {}'.format(name, self.msg)
        return name

    def __repr__(self) -> str:
        return str(self)


class InvalidEnvString(JobCalcError, TypeError):
    """Raised if parsing an environment string into a dict fails."""
    pass


class EnvDictNotFound(JobCalcError):
    """Raised if an env string is expected to return a dict, but was not
    found."""
    pass


class NotCallableError(JobCalcError, TypeError):
    """Raised if an expected type is supposed to be callable, but is not.
    """
    def __init__(self, type: Any=None) -> None:
        super().__init__('{}'.format(type.__class__.__name__))


class PercentageOutOfRange(JobCalcError, ValueError):
    """Raised if percentage is above 100 or less than 0."""

    def __init__(self, value: Any) -> None:
        super().__init__("'{}' should be a number between 0 and 100".format(
            value))


class NotIterableError(JobCalcError, TypeError):
    """Raised if an iterable is expected, but not recieved."""
    pass


class InvalidFormatter(JobCalcError, AttributeError):
    """Raised if an invalid formatter is found during calculations."""
    pass


class HourlyRateError(JobCalcError, ValueError):
    """Raised if an hourly rate is expected, but not found or 0, during
    calculations.
    """
    pass
