"""
Proxy for Views to simplify import statements and hide core package structure from client code.
"""

from signoffs.core.views import actions

__all__ = [
    "actions",
]
