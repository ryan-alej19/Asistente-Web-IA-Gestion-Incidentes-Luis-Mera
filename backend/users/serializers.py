from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    last_login_formatted = serializers.SerializerMethodField()
    date_joined_formatted = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'role', 'last_login', 'date_joined', 'last_login_formatted', 'date_joined_formatted']

    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.role
        return 'employee' # Default

    def get_last_login_formatted(self, obj):
        if obj.last_login:
            from django.utils import timezone
            return timezone.localtime(obj.last_login).strftime('%Y-%m-%d %H:%M')
        return 'Nunca'

    def get_date_joined_formatted(self, obj):
        from django.utils import timezone
        return timezone.localtime(obj.date_joined).strftime('%Y-%m-%d')

from .models import LoginAttempt

class LoginAttemptSerializer(serializers.ModelSerializer):
    timestamp_formatted = serializers.SerializerMethodField()

    class Meta:
        model = LoginAttempt
        fields = ['id', 'username', 'ip_address', 'user_agent', 'successful', 'timestamp', 'timestamp_formatted']

    def get_timestamp_formatted(self, obj):
        from django.utils import timezone
        return timezone.localtime(obj.timestamp).strftime('%Y-%m-%d %H:%M:%S')
