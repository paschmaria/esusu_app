from rest_framework import serializers

from core.models import User, Group, Profile, Membership, Transaction, Payout


class UserSerializer(serializers.ModelSerializer):
  groups = serializers.PrimaryKeyRelatedField(
                        many=True, queryset=Group.objects.all())

  class Meta:
    model = User
    fields = (
      'id',
      'first_name',
      'last_name',
      'email',
      'groups',
    )
    read_only_fields = (
      'email_confirmed'
    )