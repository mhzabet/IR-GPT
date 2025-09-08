from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core import cache
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import password_validation
User = get_user_model()
class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    


# reset password serializers.
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=250, required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value
    

class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(max_length=300,required=True)
    token = serializers.CharField(max_length=300, required=True)
    new_password = serializers.CharField(min_length=8, max_length=250, required=True, write_only=True)
    confirm_new_password = serializers.CharField(min_length=8, max_length=250, required=True, write_only=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        try:
            uid = urlsafe_base64_decode(attrs.get('uidb64')).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid UID")
        
        if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired token")      

        if new_password != confirm_new_password:
            raise serializers.ValidationError("Passwords do not match.")

        attrs['user'] = user
        return attrs
    
    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=250, required=True, write_only=True)
    new_password = serializers.CharField(max_length=250, required=True, write_only=True)
    confirm_new_password = serializers.CharField(max_length=250, required=True, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user

        if not user.check_password(attrs.get('old_password')):
            raise serializers.ValidationError({"old_password": "Old password is incorrect"})

        if attrs.get('new_password') != attrs.get('confirm_new_password'):
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match"})

        password_validation.validate_password(attrs['new_password'], user)
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user