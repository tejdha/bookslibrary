from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username','email','password','confirm_password']
        extra_kwargs = {
            "password" : {"write_only":True}
        }

    def validate(self, attrs):

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                "Password and Confirm_Password should match"
            )
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email Already Exists"
            )
        return value
    
    # def create(self, validated_data):
    #     validated_data.pop('confirm_password')
    #     user = User(username=validated_data['username'])
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user   ***** this is manual way of creating user 
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)
    
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):

    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs['identifier']
        password = attrs['password']

        if '@' in identifier:
            user = User.objects.filter(email=identifier).first()
        else:
            user = User.objects.filter(username=identifier).first()

        if user is None:
            raise serializers.ValidationError(
                "Invalid Username/Email or Password"
            )

        user = authenticate(
            username = user.username,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid Username/Email or password"
            )
        attrs['user'] = user
        return attrs

        
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name',]

class UpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username','email','first_name','last_name',]

