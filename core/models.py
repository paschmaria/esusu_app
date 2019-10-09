from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image
from uuid import uuid4

class CustomManager(BaseUserManager):
  """
    Define a model manager for User model excluding the
    username field by extending the default UserManager
  """

  use_in_migrations = True
  
  def _create_user(self, email, password, **extra_fields):
    """
      Default method for creating and saving a User with given email and password
    """
    
    if not email:
      raise ValueError('The given email must be set')
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, password=None, **extra_fields):
    """
      Create and save a regular User
    """
    
    extra_fields.setdefault('is_staff', False)
    extra_fields.setdefault('is_superuser', False)
    return self._create_user(email, password, **extra_fields)

  def create_superuser(self, email, password, **extra_fields):
    """
      Create and save a SuperUser
    """
    
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)

    if extra_fields.get('is_staff') is not True:
      raise ValueError('Superuser must have is_staff=True.')

    if extra_fields.get('is_superuser') is not True:
      raise ValueError('Superuser must have is_superuser=True.')

    return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
  """
    Custom User Model
  """

  username = None
  first_name = models.CharField(_('first name'), max_length=30)
  last_name = models.CharField(_('last name'), max_length=30)
  email = models.EmailField(
                  _("email address"),
                  max_length=100,
                  unique=True,
                  error_messages={
                    'unique': "A user with that email address already exists.",})
  email_confirmed = models.BooleanField(default=False)

  objects = CustomManager()
  
  """Set email as username field and remove it from required fields"""
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

  class Meta:
    ordering = ('email',)

class Group(models.Model):
  """
    Co-operative Group Model
  """

  CONTRIBUTION_FREQUENCY_CHOICES = [
    ('weekly', 'Weekly'),
  ]

  name = models.CharField(max_length=50)
  max_capacity = models.IntegerField()
  description = models.TextField(_("group description"), blank=True)
  logo = models.ImageField(default='group_logo.png', upload_to='group_images')
  admin = models.ForeignKey(User,
                    related_name="managed_groups",
                    on_delete=models.PROTECT)
  members = models.ManyToManyField(
                      User,
                      through='Membership',
                      through_fields=('group', 'member'),
                      related_name="coop_groups")
  contribution_amount = models.DecimalField(max_digits=10, decimal_places=2)
  contribution_frequency = models.CharField(
                    max_length=10,
                    choices=CONTRIBUTION_FREQUENCY_CHOICES,
                    default='weekly'
                  )
  current_balance = models.DecimalField(
                        max_digits=10,
                        decimal_places=2,
                        default=Decimal('0.00'))
  is_public = models.BooleanField(default=False)

  def __str__(self):
    return self.name

  # modify and/or save image in specified directory when saving model instance
  def save(self, *args, **kwargs):
    super(Group, self).save(*args, **kwargs)

    img = Image.open(self.logo.path)
    if img.height > 600 or img.width > 600:
      output_size = (600, 600)
      img.thumbnail(output_size)
      img.save(self.logo.path)

class Membership(models.Model):
  """
    Intermediate model connecting Users and Groups to manage Group memberships
  """

  group = models.ForeignKey(
              Group,
              related_name='memberships',
              on_delete=models.PROTECT)
  member = models.ForeignKey(
              User,
              related_name='memberships',
              on_delete=models.PROTECT)
  inviter = models.ForeignKey(
                User,
                on_delete=models.PROTECT,
                related_name="membership_inviter",
                null=True)
  date_invited = models.DateTimeField(auto_now_add=True)
  date_joined = models.DateTimeField(
                    auto_now=False,
                    null=True,
                    blank=True)

  def __str__(self):
    return f'New group membership for {self.member}!'

class Profile(models.Model):
  """
    User Profile Model
  """

  user = models.OneToOneField(User, on_delete=models.PROTECT)
  picture = models.ImageField(default='default.png', upload_to='profile_pics')
  current_balance = models.DecimalField(
                        max_digits=10,
                        decimal_places=2,
                        default=Decimal('0.00'))

  def __str__(self):
    return self.user.get_full_name()

  def save(self, *args, **kwargs):
    super(Profile, self).save(*args, **kwargs)

    img = Image.open(self.picture.path)
    if img.height > 400 or img.width > 400:
      output_size = (400, 400)
      img.thumbnail(output_size)
      img.save(self.picture.path)

class Transaction(models.Model):
  """
    Transaction Log: Logs when a user makes a group contribution
  """

  id = models.UUIDField(
          primary_key=True,
          default=uuid4,
          editable=False)
  value = models.DecimalField(max_digits=10, decimal_places=2)
  source = models.ForeignKey(
              User,
              on_delete=models.PROTECT,
              related_name='txn_source')
  beneficiary = models.ForeignKey(
                    Group,
                    on_delete=models.PROTECT,
                    related_name='txn_beneficiary')
  running_balance = models.DecimalField(max_digits=10, decimal_places=2) # User balance at the time of transaction.
  txn_time = models.DateTimeField(_("time of transaction"), auto_now_add=True)

  def __str__(self):
    return self.source.get_full_name()

class Payout(models.Model):
  """
    Group Payout Log: logs when a group makes a payout to its members.
  """

  id = models.UUIDField(
          primary_key=True,
          default=uuid4,
          editable=False)
  amount = models.DecimalField(max_digits=10, decimal_places=2) # payout amount
  source = models.ForeignKey(
              Group,
              on_delete=models.PROTECT,
              related_name='pyt_source')
  beneficiary = models.ForeignKey(
                    User,
                    on_delete=models.PROTECT,
                    related_name='pyt_beneficiary')
  running_balance = models.DecimalField(max_digits=10, decimal_places=2) # Group balance at the time of transaction.
  pyt_time = models.DateTimeField(_("time of payout"), auto_now_add=True)

  def __str__(self):
    return self.source