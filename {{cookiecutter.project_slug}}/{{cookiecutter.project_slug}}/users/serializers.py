# -*- coding: utf-8 -*-

"""Serializers for users."""

from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import TokenError

from {{ cookiecutter.project_slug }}.users.models import User
from {{ cookiecutter.project_slug }}.users.validators import CfValidator


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User."""

    is_staff = serializers.BooleanField(required=False)

    class Meta:
        """Metadata for serializer."""

        model = User
        fields = [
            'id',
            'name',
            'first_name',
            'last_name',
            'cf',
            'is_privacy_accepted',
            'privacy_accepted_datetime',
            'is_terms_and_conditions_accepted',
            'terms_and_conditions_accepted_datetime',
            'is_marketing_accepted',
            'marketing_accepted_datetime',
            'is_staff',
        ]
        read_only_fields = [
            'reference_code',
            'privacy_accepted_datetime',
            'terms_and_conditions_accepted_datetime',
            'marketing_accepted_datetime',
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'cf': {
                'validators': [
                    CfValidator(),
                    UniqueValidator(queryset=User.objects.all()),
                ],
            },
        }

    def validate(self, data_sent):
        """Check if the data sent are valid."""
        user = self.context['request'].user
        if data_sent.get('is_staff', False) and (not user.is_staff):
            raise serializers.ValidationError({
                'is_staff': ['Only staff user can grant privileges.'],
            })

        return super().validate(data_sent)

    def create(self, validated_data):
        """Override creation."""
        valid_data = validated_data.copy()
        return User.objects.create_user(**valid_data, is_active=False)


class UserDetailSerializer(UserSerializer):
    """Serializer for user details."""

    class Meta:
        """Metadata for serializer."""

        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields
        read_only_fields = UserSerializer.Meta.read_only_fields
        extra_kwargs = UserSerializer.Meta.extra_kwargs


class UserRegistrationSerializer(UserSerializer):
    """Serializer for user regitration."""

    class Meta:
        """Metadata for UserRegistrationSerializer."""

        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + [
            'username',
            'email',
            'password',
        ]
        read_only_fields = UserSerializer.Meta.read_only_fields
        extra_kwargs = {
            **UserSerializer.Meta.extra_kwargs,  # type: ignore
            'password': {'write_only': True},
        }

    def validate(self, data_sent):
        """Check if the data sent are valid."""
        now = timezone.now()
        if not data_sent.get('is_privacy_accepted', False):
            raise serializers.ValidationError({
                'is_privacy_accepted': ['Privacy should be accepted'],
            })
        data_sent['privacy_accepted_datetime'] = now

        if not data_sent.get('is_terms_and_conditions_accepted', False):
            raise serializers.ValidationError({
                'is_terms_and_conditions_accepted': ['Terms and conditions should be accepted'],
            })
        data_sent['terms_and_conditions_accepted_datetime'] = now

        if data_sent.get('is_marketing_accepted', False):
            data_sent['marketing_accepted_datetime'] = now

        return super().validate(data_sent)


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout action.

    Originally developed by orehush (https://gist.github.com/orehush/667c79b28fdc94f86746bd15694d1167).
    """

    refresh = serializers.CharField(write_only=True)

    default_error_messages = {
        'bad_token': 'Token is invalid or expired',
    }

    def validate(self, data_sent):
        """Validate refresh token passed."""
        try:
            RefreshToken(data_sent['refresh'])
        except TokenError:
            raise serializers.ValidationError({
                'refresh': ['Refresh token not valid or expired.'],
            })

        return super().validate(data_sent)

    def save(self):
        """Put in blacklist the refresh token."""
        RefreshToken(self.validated_data['refresh']).blacklist()
