"""
Proxy for core.models to simplify import statements and hide core package structure from client code.
"""

from django.apps import apps

from signoffs.core.models import (
    AbstractApprovalSignet,
    AbstractApprovalStamp,
    AbstractRevokedSignet,
    AbstractSignet,
)
from signoffs.core.models.fields import (
    ApprovalField,
    ApprovalSignoffSet,
    ApprovalSignoffSingle,
    SignoffField,
    SignoffSet,
    SignoffSingle,
)
from signoffs.core.models.fields import RelatedApprovalDescriptor as RelatedApproval
from signoffs.core.models.fields import RelatedSignoffDescriptor as RelatedSignoff

__all__ = [
    "AbstractApprovalSignet",
    "AbstractApprovalStamp",
    "AbstractRevokedSignet",
    "AbstractSignet",
    "ApprovalField",
    "ApprovalSignoffSet",
    "ApprovalSignoffSingle",
    "SignoffField",
    "SignoffSet",
    "SignoffSingle",
    "RelatedApproval",
    "RelatedSignoff",
]

if apps.is_installed("signoffs.contrib.signets"):
    from signoffs.contrib.signets.models import RevokedSignet, Signet

    __all__ += [
        "RevokedSignet",
        "Signet",
    ]

if apps.is_installed("signoffs.contrib.approvals"):
    from signoffs.contrib.approvals.models import RevokedSignet as RevokedApprovalSignet
    from signoffs.contrib.approvals.models import Signet as ApprovalSignet
    from signoffs.contrib.approvals.models import Stamp

    __all__ += [
        "RevokedApprovalSignet",
        "ApprovalSignet",
        "Stamp",
    ]
