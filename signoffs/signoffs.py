"""
Proxy for Signoff Types to simplify import statements and hide core package structure from client code.
"""

from django.apps import apps

from .core import signing_order, utils
from .core.forms import (
    SignoffFormsManager,
    SignoffTypeForms,
)
from .core.renderers import (
    SignoffInstanceRenderer,
    SignoffRenderer,
)
from .core.signoffs import (
    AbstractSignoff,
    BaseSignoff,
    SignoffLogic,
)
from .core.urls import (
    SignoffInstanceUrls,
    SignoffUrlsManager,
)

__all__ = [
    "signing_order",
    "utils",
    "SignoffFormsManager",
    "SignoffTypeForms",
    "SignoffInstanceRenderer",
    "SignoffRenderer",
    "AbstractSignoff",
    "BaseSignoff",
    "SignoffLogic",
    "SignoffInstanceUrls",
    "SignoffUrlsManager",
]

if apps.is_installed("signoffs.contrib.signets"):
    from .contrib.signets.signoffs import (
        IrrevokableSignoff,
        RevokableSignoff,
        SimpleSignoff,
    )

    __all__ += [
        "IrrevokableSignoff",
        "RevokableSignoff",
        "SimpleSignoff",
    ]
