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
        fields = ('id', 'email', 'role', 'phone')
        read_only_fields = ('id', 'email', 'role', 'phone')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )

    def validate(self, attrs):
        user = self.context["request"].user

        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({
                "old_password": "Old password is incorrect."
            })

        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user