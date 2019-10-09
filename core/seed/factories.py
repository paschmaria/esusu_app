from django.core.files.base import ContentFile
from faker import Faker

import factory, random

from core.models import (User, Group, Membership,
                            Profile, Transaction)


# faker = Faker()

class UserFactory(factory.DjangoModelFactory):
  """
    Factory for creating User instances used in writing tests
    Generates random users everytime an instance is generated.
  """
  
  class Meta:
    model = User

  first_name = factory.Faker('first_name')
  last_name = factory.Faker('last_name')
  email = factory.Faker('email')
  password = 'NewUser'
  email_confirmed = True

CONTRIBUTION_FREQUENCY = [x[0] for x in Group.CONTRIBUTION_FREQUENCY_CHOICES]
class GroupFactory(factory.DjangoModelFactory):
  """
    Factory for creating Cooperative Group Instances used in tests
  """

  class Meta:
    model = Group

  name = factory.Sequence(lambda n: "Group #%s" % n)
  # max_capacity = factory.LazyAttribute(
  #             lambda _: faker.pyint(
  #               min_value=0,
  #               max_value=500,
  #               step=1))
  description = factory.Faker('')
  admin = factory.SubFactory(UserFactory)
  logo = factory.LazyAttribute(
              lambda _: ContentFile(
                factory.django.ImageField()._make_data(
                  {'width': 300, 'height': 300}
                ), 'logo.png'))
  contribution_frequency = factory.LazyFunction(
                                lambda x: random.choice(CONTRIBUTION_FREQUENCY))
  # current_balance = factory.LazyAttribute(
  #                         lambda _: faker.pyint(
  #                           min_value=0,
  #                           max_value=9999,
  #                           step=1))
  is_public = True
  
  @factory.post_generation
  def members(self, create, extracted, **kwargs):
    if not create:
      # Simple build, do nothing.
      return

    if extracted:
      # A list of members were passed in, use them
      for member in extracted:
        self.members.add(member)

class MembershipFactory(factory.DjangoModelFactory):
  """
    Factory for creating Cooperative Group Membership Instances
  """

  class Meta:
    model = Membership

  group = factory.SubFactory(GroupFactory)
  member = factory.SubFactory(UserFactory)
  inviter = factory.SubFactory(UserFactory)

class ProfileFactory(factory.DjangoModelFactory):
  """
    Factory for creating User Profile Instances
  """

  class Meta:
    model = Profile

  user = factory.SubFactory(UserFactory)
  picture = factory.LazyAttribute(
                lambda _: ContentFile(
                  factory.django.ImageField()._make_data(
                    {'width': 300, 'height': 300}
                  ), 'profile_pic.png'))
  # current_balance = factory.LazyAttribute(
  #                       lambda _: faker.pyint(
  #                         min_value=0,
  #                         max_value=9999,
  #                         step=1))

class TransactionFactory(factory.DjangoModelFactory):
  """
    Factory for creating Transaction Instances

    value: Amt transferred during transaction
    running_balance: Amt left in sender's account after transaction
  """

  class Meta:
    model = Transaction

  # value = factory.LazyAttribute(
  #             lambda _: faker.pyint(
  #               min_value=0,
  #               max_value=9999,
  #               step=1))
  source = factory.SubFactory(UserFactory)
  beneficiary = factory.SubFactory(GroupFactory)
  # running_balance = factory.LazyAttribute(
  #                       lambda _: faker.pyint(
  #                         min_value=0,
  #                         max_value=9999,
  #                         step=1))