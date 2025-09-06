from rest_framework import serializers
from .models import CustomUser


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