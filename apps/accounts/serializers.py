from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'role')

        def validate_role(self, value):
            allowed_roles = [CustomUser.Role.CLIENT, CustomUser.Role.FREELANCER]
            if value not in allowed_roles:
                raise serializers.ValidationError(f"Invalid role for self-registration: {value}")
            return value
        
        def validate_email(self, value):
            return value.strip().lower()
        
        def create(self, validated_data):
            return CustomUser.objects.create_user(**validated_data)
        
class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'role', 'phone', 'created_at')
        read_only_fields = ('id', 'email', 'role', 'phone', 'created_at')
        