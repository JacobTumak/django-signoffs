"""
Proxy for Approval Process to simplify import statements and hide core package structure from client code.
"""

from signoffs.core.process import (
    ApprovalsProcess,
    BasicApprovalProcess,
    FsmApprovalProcess,
    FsmApprovalsProcess,
    TransactionRevoke,
    TransactionSave,
    user_can_revoke_approval,
)

__all__ = [
    "ApprovalsProcess",
    "BasicApprovalProcess",
    "FsmApprovalProcess",
    "FsmApprovalsProcess",
    "TransactionRevoke",
    "TransactionSave",
    "user_can_revoke_approval",
]
