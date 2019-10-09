from django.test import TestCase
from django.contrib.auth import get_user_model

from core.seed.factories import (UserFactory, GroupFactory, MembershipFactory,
                                        ProfileFactory, TransactionFactory)


class CustomManagerTest(TestCase):
  """
    Unit tests for Custom User Manager
  """
  
  def test_create_user(self):
    User = get_user_model()
    user = User.objects.create_user(email='normal@user.com', password='NewUser')
    self.assertEqual(user.email, 'normal@user.com')
    self.assertTrue(user.is_active)
    self.assertFalse(user.is_staff)
    self.assertFalse(user.is_superuser)

    try:
      self.assertIsNone(user.username)
    except AttributeError:
      pass

    with self.assertRaises(TypeError):
      User.objects.create_user()
    with self.assertRaises(ValueError):
      User.objects.create_user(email='')
    with self.assertRaises(ValueError):
      User.objects.create_user(email='', password="NewUser")

  def test_create_superuser(self):
    User = get_user_model()
    admin_user = User.objects.create_superuser('super@user.com', 'NewUser')
    self.assertEqual(admin_user.email, 'super@user.com')
    self.assertTrue(admin_user.is_active)
    self.assertTrue(admin_user.is_staff)
    self.assertTrue(admin_user.is_superuser)

    try:
      self.assertIsNone(admin_user.username)
    except AttributeError:
      pass

    with self.assertRaises(ValueError):
      User.objects.create_superuser(email='super@user.com', password='NewUser', is_superuser=False)

class UserModelTest(TestCase):
  """
    Unit tests for User Model
  """

  def setUp(self):
    self.user = UserFactory()

  # test that username field has no value
  def test_username_field_is_none(self):
    self.assertIsNone(self.user.username)

  # test field error messages
  def test_email_field_errors(self):
    error_messages = self.user._meta.get_field('email').error_messages
    self.assertEqual(error_messages['unique'], 'A user with that email address already exists.')

class GroupModelTest(TestCase):
  """
    Unit tests for Co-operative Group Model
  """

  def setUp(self):
    self.users = UserFactory.create_batch(5)
    self.group = GroupFactory(admin=self.users[0], members=(*self.users,))

  # test that model string representation matches expectations
  def test_string_representation(self):
    self.assertEqual(str(self.group), self.group.name)

class MembershipModelTest(TestCase):
  """
    Unit tests for Group Membership Model
  """

  def setUp(self):
    self.users = UserFactory.create_batch(5)
    self.user1_group = GroupFactory(admin=self.users[0])
    self.user2_group = GroupFactory(admin=self.users[1])

    # add all users to each group
    for user in self.users:
      MembershipFactory(group=self.user1_group, member=user)
      MembershipFactory(group=self.user2_group, member=user)

  # test that a user is a member of both groups
  def test_user_membership(self):
    self.assertEqual(list(self.users[2].coop_groups.all()), [self.user1_group, self.user2_group])

  # test that a user is an admin of a group
  def test_group_admin(self):
    self.assertEqual(self.user1_group.admin, self.users[0])

  # test that model string representation matches expectations
  def test_string_representation(self):
    membership = MembershipFactory()
    self.assertEqual(str(membership), f'New group membership for {membership.member}!')

class ProfileModelTest(TestCase):
  """
    Unit tests for Profile Model
  """

  def setUp(self):
    self.user = UserFactory()
    self.profile = ProfileFactory(user=self.user)
    
  def test_string_representation(self):
    self.assertEqual(str(self.profile), self.profile.user.get_full_name())

class TransactionModelTest(TestCase):
  """
    Unit tests for the Transaction Model
  """

  def setUp(self):
    self.users = UserFactory.create_batch(5)
    self.group = GroupFactory(admin=self.users[0], members=(*self.users,))
    self.transaction = TransactionFactory(source=self.users[2], beneficiary=self.group)

  def test_string_representation(self):
    self.assertEqual(str(self.transaction), self.transaction.source.get_full_name())
