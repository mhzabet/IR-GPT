from rest_framework import serializers
from .models import CustomUser
from django.core import cache

class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'preferred_lang',
            'avatar',
            'is_active',
            ]

class RegisterUserSerializer(BaseUserSerializer):
    password = serializers.CharField(max_length=250, required=True, write_only=True)
    password2 = serializers.CharField(max_length=250, required=True, write_only=True)

    class Meta:
        model = BaseUserSerializer.Meta.model
        fields = BaseUserSerializer.Meta.fields + ['password','password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password":"Password fields didn't match."})
        return super().validate(attrs)
    
    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    


# reset password serializers.
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=250, required=True)
    
    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value
    

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=250, required=True)
    token = serializers.CharField(max_length=300, required=True)
    new_password = serializers.CharField(min_length=8, max_length=250, required=True, write_only=True)
    confirm_new_password = serializers.CharField(min_length=8, max_length=250, required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        token = attrs.get('token')
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        saved_token = cache.get(f"password-reset:{email}")
        if saved_token != token:
            raise serializers.ValidationError("Invalid or expired token.")
        if new_password != confirm_new_password:
            raise serializers.ValidationError("Passwords do not match.")

        return attrs
    
    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = CustomUser.objects.get(email=email)
        user.set_password(new_password)
        
        # delete cached token.
        cache.delete(f"password-reset:{email}")
        return user