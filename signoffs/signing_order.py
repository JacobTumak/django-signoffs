"""
Proxy for Signoff Signing Order to simplify import statements and hide core package structure from client code.
"""

from signoffs.core.signing_order.signing_order import (
    SigningOrder,
    SigningOrderStrategyProtocol,
)
from signoffs.core.signing_order.signoff_pattern import (
    AnyOneOf,
    AtLeastN,
    ExactlyN,
    ExactlyOne,
    InParallel,
    InSeries,
    OneOrMore,
    Optional,
    ZeroOrMore,
)

__all__ = [
    "SigningOrder",
    "SigningOrderStrategyProtocol",
    "AnyOneOf",
    "AtLeastN",
    "ExactlyN",
    "ExactlyOne",
    "InParallel",
    "InSeries",
    "OneOrMore",
    "Optional",
    "ZeroOrMore",
]
