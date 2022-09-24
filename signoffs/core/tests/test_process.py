"""
App-independent UNIT tests for underlying approval process support classes - no app logic
"""
import django_fsm as fsm
from django.test import TestCase
from django.db import models

import signoffs.core.signing_order as so
from signoffs.registry import register
from signoffs.core import process
from signoffs.core.models.fields import RelatedApprovalDescriptor, ApprovalField, ApprovalSignoffSingle

from signoffs.core.tests.models import ApprovalSignoff, AbstractLeaveApproval
from signoffs.core.tests import fixtures


# Basic tests - no models, no state changes

@register(id='test.process.application')
class Application(AbstractLeaveApproval):

    employee_signoff = ApprovalSignoffSingle(
        ApprovalSignoff.register(id='test.process.application.employee_signoff')
    )


@register(id='test.process.authorization')
class Authorization(AbstractLeaveApproval):

    hr_signoff_type = ApprovalSignoff.register(id='test.process.authorization.hr_signoff')
    mngmt_signoff_type = ApprovalSignoff.register(id='test.process.authorization.mngmt_signoff')



class ApprovalTransitionTests(TestCase):

    def test_approval_transition(self):
        t = process.ApprovalTransition(approval_id='test.process.application',
                                       approve=self.test_approval_transition)
        self.assertEqual(t.approval_id, 'test.process.application')
        self.assertEqual(t.approve_name, 'test_approval_transition')
        self.assertIsNone(t.revoke)
        self.assertEqual(t.revoke_name, '')

    def test_approval_transition_registry(self):
        r = process.ApprovalTransitionRegistry()
        r.add_approval(Application)  # adding entry sets the ordering, even if no transitions given
        r.add_approve_transition(Authorization, self.test_approval_transition_registry) # add transition to new item
        r.add_approve_transition(Application, self.test_approval_transition)  # go back an add transition to exsiting
        r.add_revoke_transition(Authorization, self.test_approval_transition_registry)
        self.assertEqual(r.get(Authorization).approve, self.test_approval_transition_registry)
        self.assertEqual(r.get(Authorization).revoke, self.test_approval_transition_registry)
        self.assertEqual(len(r.approval_order()), 2)
        self.assertListEqual(r.approval_order(), [Application.id, Authorization.id])
        self.assertListEqual([t.approve for t in r], [self.test_approval_transition, self.test_approval_transition_registry])  # Test iter


class ProtoProcess:
    """ The inkling of the components an approval process will be made up of """

    # introspection logic in BoundApprovalSequence requires class variables with ApprovalType same name as instance variables
    # Normally this is handled by declaring these related approvals using an ApprovalField or RelatedApprovalDescriptor
    #  --> this is not a useful code pattern - for unit testing only!
    approval1 = Application
    approval2 = Authorization

    def __init__(self):
        # normally approval instance would be generated by a RelatedApprovalDescriptor
        self.approval1 = Application()
        self.approval2 = Authorization()

        # actual processes would not manage the transition registry themselves - this is for unit testing only
        self.reg = process.ApprovalTransitionRegistry()
        self.reg.add_approve_transition(self.approval1, self.transition1)
        self.reg.add_approve_transition(self.approval2, self.transition2)
        self.reg.add_revoke_transition(self.approval1, self.revoke_transition)

    def transition1(self, approval):
        print("Transition 1 for ", approval)

    def transition2(self, approval):
        print("Transition 2 for ", approval)

    def revoke_transition(self, approval):
        print("Revoke Transition for ", approval)

    def get_approval_sequence(self):
        return process.BoundApprovalSequence(self, ordering=self.reg.approval_order())

    def get_approval_actions_registry(self):
        return process.ApprovalActionsRegistry(self, self.reg)


class ApprovalSequenceTests(TestCase):
    def test_transition_registry(self):
        test = ProtoProcess()
        self.assertEqual(test.reg.get(test.approval1).approve,  test.transition1)
        self.assertIsNone(test.reg.get('NotExists'))

    def test_approval_sequence(self):
        test = ProtoProcess()
        seq = test.get_approval_sequence()
        self.assertDictEqual(seq, {
            'approval1': test.approval1,
            'approval2': test.approval2
        })


class BasicApprovalActionsRegistryTests(TestCase):
    def setUp(self):
        super().setUp()
        process = ProtoProcess()
        self.actions_registry = process.get_approval_actions_registry()
        self.process = process

    def test_approval_sequence(self):
        self.assertDictEqual(self.actions_registry.seq, {
            'approval1': self.process.approval1,
            'approval2': self.process.approval2
        })

    def test_get_all_approvals(self):
        self.assertListEqual(self.actions_registry.get_all_approvals(), [self.process.approval1, self.process.approval2])

    def test_get_approved_approvals(self):
        self.assertListEqual(self.actions_registry.get_approved_approvals(), [])

    def test_get_unapproved_approvals(self):
        self.assertListEqual(self.actions_registry.get_unapproved_approvals(), [self.process.approval1, self.process.approval2])

    def test_get_next_approval(self):
        self.assertEqual(self.actions_registry.get_next_approval(), self.process.approval1)

    def test_next_approval_is_signed(self):
        self.assertFalse(self.actions_registry.next_approval_is_signed())

    def test_get_previous_approval(self):
        self.assertEqual(self.actions_registry.get_previous_approval(), None)

    def test_get_available_approvals(self):
        self.assertListEqual(self.actions_registry.get_available_approvals(), [self.process.approval1, ])

    def test_get_next_available_approval(self):
        self.assertEqual(self.actions_registry.get_next_available_approval(), self.process.approval1)

    def test_get_revokable_approvals(self):
        self.assertListEqual(self.actions_registry.get_revokable_approvals(), [])

    def test_get_next_revokable_approval(self):
        self.assertEqual(self.actions_registry.get_next_revokable_approval(), None)

    def test_bound_approve_transition(self):
        self.assertEqual(self.actions_registry.bound_approve_transition(self.process.approval1), self.process.transition1)
        self.assertEqual(self.actions_registry.bound_approve_transition(self.process.approval2), self.process.transition2)

    def test_bound_revoke_transition(self):
        self.assertEqual(self.actions_registry.bound_revoke_transition(self.process.approval1), self.process.revoke_transition)
        self.assertEqual(self.actions_registry.bound_revoke_transition(self.process.approval2), None)


# Tests requiring a model with state changes


@register(id='test.process.approval1')
class Approval1(AbstractLeaveApproval):

    signoff1 = ApprovalSignoffSingle(
        ApprovalSignoff.register(id='test.process.approval1.signoff1')
    )

    def is_complete(self):
        """ Customize logic for determining if Approval signoffs are complete and ready to be approved. """
        return self.signoff1.get().is_signed()

    def sign_approval(self, user):
        if self.signoff1.can_sign(user):
            self.signoff1.create(user=user)


@register(id='test.process.approval2')
class Approval2(AbstractLeaveApproval):

    signoff1 = ApprovalSignoff.register(id='test.process.approval2.signoff1')
    signoff2 = ApprovalSignoff.register(id='test.process.approval2.signoff2')

    signing_order = so.SigningOrder(
        so.AtLeastN(signoff1, n=1),
        signoff2
    )

    def sign_approval(self, user):
        next = self.next_signoffs(for_user=user)
        if next and not self.is_approved() and not self.has_signed(user):
            next[-1].sign(user)  # Arbitrarily approve "most nextest" signoff on the approval


class NonFsmApprovalProcess(models.Model):
    """ An Approval Process model where transitions and approval sequencing are handled by app logic - no ordering """

    class States(models.TextChoices):
        STATE0 = 'Initiated'
        STATE1 = 'State 1'
        STATE2 = 'State 2'

    state = str(States.STATE0)

    approval1, approval1_stamp = ApprovalField(Approval1)
    approval2, approval2_stamp = ApprovalField(Approval2)

    actions = process.ApprovalActions()  # optionally list approvals in order, default is order they are registered below

    @actions.register_approve_transition(approval1)
    def transition1(self, approval):
        self.state = self.States.STATE1
        print("Transition 1", self.state, self.approval1)

    @actions.register_approve_transition(approval2)
    def transition2(self, approval):
        self.state = self.States.STATE2
        print("Transition 2", self.state, self.approval2)

    @actions.register_revoke_transition(approval1)
    def revoke1(self, approval):
        self.state = self.States.STATE0
        print("Revoke Transition 1", self.state, self.approval1)

    @actions.register_revoke_transition(approval2)
    def revoke2(self, approval):
        self.state = self.States.STATE1
        print("Revoke Transition 2", self.state, self.approval2)

    def sign_and_approve_approval1(self):
        u = fixtures.get_user()
        self.approval1.sign_approval(u)
        self.actions.try_approve_transition(self.approval1, u)

    def sign_and_approve_approval2(self):
        u1 = fixtures.get_user()
        self.approval2.sign_approval(u1)
        u2 = fixtures.get_user()
        self.approval2.sign_approval(u2)
        self.actions.try_approve_transition(self.approval2, u2)


class NonFsmApprovalActionsTests(TestCase):
    def setUp(self):
        super().setUp()
        process = NonFsmApprovalProcess()
        self.process = process

    def test_can_proceed(self):
        self.assertTrue(self.process.actions.can_proceed(self.process.approval1))
        self.assertFalse(self.process.actions.can_proceed(self.process.approval2))

        self.process.sign_and_approve_approval1()
        self.assertFalse(self.process.actions.can_proceed(self.process.approval1))
        self.assertTrue(self.process.actions.can_proceed(self.process.approval2))

    def test_user_can_proceed(self):
        u = fixtures.get_user()
        self.assertTrue(self.process.actions.user_can_proceed(self.process.approval1, u))
        self.assertFalse(self.process.actions.user_can_proceed(self.process.approval2, u))

    def test_can_do_approve_transition(self):
        u = fixtures.get_user()
        self.assertFalse(self.process.actions.can_do_approve_transition(self.process.approval1, u))

        self.process.approval1.sign_approval(u)
        self.assertTrue(self.process.actions.can_do_approve_transition(self.process.approval1, u))
        self.assertFalse(self.process.actions.can_do_approve_transition(self.process.approval2, u))

    def test_can_revoke(self):
        self.assertFalse(self.process.actions.can_revoke(self.process.approval1))
        self.assertFalse(self.process.actions.can_revoke(self.process.approval2))

        self.process.sign_and_approve_approval1()
        self.assertTrue(self.process.actions.can_revoke(self.process.approval1))

    def test_has_revoke_transition_perm(self):
        u = fixtures.get_user()
        self.assertFalse(self.process.actions.has_revoke_transition_perm(self.process.approval1, u))
        self.assertFalse(self.process.actions.has_revoke_transition_perm(self.process.approval2, u))

        self.process.sign_and_approve_approval1()
        self.assertTrue(self.process.actions.has_revoke_transition_perm(self.process.approval1, u))

    def test_user_can_revoke(self):
        u = fixtures.get_user()
        self.assertFalse(self.process.actions.user_can_revoke(self.process.approval1, u))
        self.assertFalse(self.process.actions.user_can_revoke(self.process.approval2, u))

    def test_can_do_revoke_transition(self):
        u = fixtures.get_user()
        self.assertFalse(self.process.actions.can_do_revoke_transition(self.process.approval1, u))

        self.process.sign_and_approve_approval1()
        self.assertTrue(self.process.actions.can_do_revoke_transition(self.process.approval1, u))
        self.assertFalse(self.process.actions.can_do_revoke_transition(self.process.approval2, u))

    def test_try_approve_transition(self):
        u = fixtures.get_user()
        u2 = fixtures.get_user()
        self.assertFalse(self.process.actions.try_approve_transition(self.process.approval1, u))

        self.process.approval1.sign_approval(u)
        self.assertTrue(self.process.actions.try_approve_transition(self.process.approval1, u))
        self.assertEqual(self.process.state, self.process.States.STATE1)

        self.process.approval2.sign_approval(u)
        self.assertFalse(self.process.actions.try_approve_transition(self.process.approval2, u))
        self.process.approval2.sign_approval(u2)
        self.assertTrue(self.process.actions.try_approve_transition(self.process.approval2, u2))
        self.assertEqual(self.process.state, self.process.States.STATE2)


    def test_try_revoke_transition(self):
        u = fixtures.get_user()
        self.assertFalse(self.process.actions.try_revoke_transition(self.process.approval1, u))

        self.process.sign_and_approve_approval1()
        self.process.sign_and_approve_approval2()
        self.assertEqual(self.process.state, self.process.States.STATE2)

        self.assertFalse(self.process.actions.try_revoke_transition(self.process.approval1, u))
        self.assertTrue(self.process.actions.try_revoke_transition(self.process.approval2, u))
        self.assertEqual(self.process.state, self.process.States.STATE1)

        self.assertFalse(self.process.actions.try_revoke_transition(self.process.approval2, u))
        self.assertTrue(self.process.actions.try_revoke_transition(self.process.approval1, u))
        self.assertEqual(self.process.state, self.process.States.STATE0)


# FSM Approval Process TODO: add transition conditions and permissions to show how this changes results


class FsmApprovalProcess(models.Model):
    """ An Approval Process model where transitions and approval sequencing are defined by FSM """

    class States(models.TextChoices):
        STATE0 = 'Initiated'
        STATE1 = 'State 1'
        STATE2 = 'State 2'

    state = fsm.FSMField(choices=States.choices, default=States.STATE0)

    approval1, approval1_stamp = ApprovalField(Approval1)
    approval2, approval2_stamp = ApprovalField(Approval2)

    actions = process.FsmApprovalActions()

    @actions.register_approve_transition(approval1)
    @fsm.transition(state, source=States.STATE0, target=States.STATE1)
    def transition1(self, approval):
        print("FSM Transition 1", self.state, self.approval1)

    @actions.register_approve_transition(approval2)
    @fsm.transition(state, source=States.STATE1, target=States.STATE2)
    def transition2(self, approval):
        print("FSM Transition 2", self.state, self.approval2)

    @actions.register_revoke_transition(approval1)
    @fsm.transition(state, source=States.STATE1, target=States.STATE0)
    def revoke1(self, approval):
        print("FSM Revoke Transition 1", self.state, self.approval1)

    @actions.register_revoke_transition(approval2)
    @fsm.transition(state, source=States.STATE2, target=States.STATE1)
    def revoke2(self, approval):
        print("FSM Revoke Transition 2", self.state, self.approval2)

    def sign_and_approve_approval1(self):
        u = fixtures.get_user()
        self.approval1.sign_approval(u)
        self.actions.try_approve_transition(self.approval1, u)

    def sign_and_approve_approval2(self):
        u1 = fixtures.get_user()
        self.approval2.sign_approval(u1)
        u2 = fixtures.get_user()
        self.approval2.sign_approval(u2)
        self.actions.try_approve_transition(self.approval2, u2)


class FsmApprovalActionsTests(TestCase):
    def setUp(self):
        super().setUp()
        process = FsmApprovalProcess()
        self.process = process

    def test_can_proceed(self):
        self.assertTrue(self.process.actions.can_proceed(self.process.approval1))
        self.assertFalse(self.process.actions.can_proceed(self.process.approval2))

        self.process.sign_and_approve_approval1()
        self.assertFalse(self.process.actions.can_proceed(self.process.approval1))
        self.assertTrue(self.process.actions.can_proceed(self.process.approval2))

    def test_user_can_proceed(self):
        u = fixtures.get_user()
        self.assertTrue(self.process.actions.user_can_proceed(self.process.approval1, u))
        self.assertFalse(self.process.actions.user_can_proceed(self.process.approval2, u))

    def test_can_do_approve_transition(self):
        u = fixtures.get_user()
        self.assertFalse(self.process.actions.can_do_approve_transition(self.process.approval1, u))

        self.process.approval1.sign_approval(u)
        self.assertTrue(self.process.actions.can_do_approve_transition(self.process.approval1, u))
        self.assertFalse(self.process.actions.can_do_approve_transition(self.process.approval2, u))

    def test_can_revoke(self):
        self.assertFalse(self.process.actions.can_revoke(self.process.approval1))
        self.assertFalse(self.process.actions.can_revoke(self.process.approval2))

        self.process.sign_and_approve_approval1()
        self.assertTrue(self.process.actions.can_revoke(self.process.approval1))

    def test_has_revoke_transition_perm(self):
        u = fixtures.get_user()
        self.assertFalse(self.process.actions.has_revoke_transition_perm(self.process.approval1, u))
        self.assertFalse(self.process.actions.has_revoke_transition_perm(self.process.approval2, u))

        self.process.sign_and_approve_approval1()
        self.assertTrue(self.process.actions.has_revoke_transition_perm(self.process.approval1, u))

    def test_user_can_revoke(self):
        u = fixtures.get_user()
        self.assertFalse(self.process.actions.user_can_revoke(self.process.approval1, u))
        self.assertFalse(self.process.actions.user_can_revoke(self.process.approval2, u))

    def test_can_do_revoke_transition(self):
        u = fixtures.get_user()
        self.assertFalse(self.process.actions.can_do_revoke_transition(self.process.approval1, u))

        self.process.sign_and_approve_approval1()
        self.assertTrue(self.process.actions.can_do_revoke_transition(self.process.approval1, u))
        self.assertFalse(self.process.actions.can_do_revoke_transition(self.process.approval2, u))

    def test_try_approve_transition(self):
        u = fixtures.get_user()
        u2 = fixtures.get_user()
        self.assertFalse(self.process.actions.try_approve_transition(self.process.approval1, u))

        self.process.approval1.sign_approval(u)
        self.assertTrue(self.process.actions.try_approve_transition(self.process.approval1, u))
        self.assertEqual(self.process.state, self.process.States.STATE1)

        self.process.approval2.sign_approval(u)
        self.assertFalse(self.process.actions.try_approve_transition(self.process.approval2, u))
        self.process.approval2.sign_approval(u2)
        self.assertTrue(self.process.actions.try_approve_transition(self.process.approval2, u2))
        self.assertEqual(self.process.state, self.process.States.STATE2)


    def test_try_revoke_transition(self):
        u = fixtures.get_user()
        self.assertFalse(self.process.actions.try_revoke_transition(self.process.approval1, u))

        self.process.sign_and_approve_approval1()
        self.process.sign_and_approve_approval2()
        self.assertEqual(self.process.state, self.process.States.STATE2)

        self.assertFalse(self.process.actions.try_revoke_transition(self.process.approval1, u))
        self.assertTrue(self.process.actions.try_revoke_transition(self.process.approval2, u))
        self.assertEqual(self.process.state, self.process.States.STATE1)

        self.assertFalse(self.process.actions.try_revoke_transition(self.process.approval2, u))
        self.assertTrue(self.process.actions.try_revoke_transition(self.process.approval1, u))
        self.assertEqual(self.process.state, self.process.States.STATE0)
