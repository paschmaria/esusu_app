from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Group, Membership, Profile, Transaction, Payout
from .forms import RegisterForm


class UserAdmin(BaseUserAdmin):
  """Define admin model for custom User model with no email field"""

  add_form = RegisterForm
  fieldsets = (
      (None, {'fields': ('email', 'password')}),
      (_('Personal info'), {'fields': ('first_name', 'last_name')}),
      (_('Permissions'), {'fields': ('is_active', 'email_confirmed', 'is_staff', 'is_superuser',
                                      'groups', 'user_permissions')}),
      (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
  )
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
      }),
  )
  list_display = ('email', 'first_name', 'last_name', 'is_active')
  search_fields = ('email', 'first_name', 'last_name')
  ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(Group)
admin.site.register(Membership)
admin.site.register(Profile)
admin.site.register(Transaction)
admin.site.register(Payout)