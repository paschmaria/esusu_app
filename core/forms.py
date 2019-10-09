from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import User, Group, Profile, Membership, Transaction

class RegisterForm(UserCreationForm):
  """Form for registering new users"""
  
  class Meta(UserCreationForm.Meta):
    model = User
    fields = (
      'first_name',
      'last_name',
      'email',
      'password1',
      'password2',
    )
  
  """save all form data"""
  def save(self, commit=True):
    user = super(RegisterForm, self).save(commit=False)
    user.first_name = self.cleaned_data['first_name']
    user.last_name = self.cleaned_data['last_name']
    user.email_address = self.cleaned_data['email']
    if commit:
        user.save()
    return user

class LoginForm(AuthenticationForm):
  remember_me = forms.BooleanField()
  
  def confirm_login_allowed(self, user):
    if not user.is_active:
      raise forms.ValidationError(
        _("This account hasn't been activated."),
        code='inactive',
      )

class GroupCreationForm(forms.ModelForm):
  
  class Meta:
    model = Group
    fields = (
      'name',
      'max_capacity',
      'is_public',
      'logo',
      'description',
      'contribution_amount',
      'contribution_frequency',
    )