from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'password', 'region', 'active_status', 'place_holder']
        extra_kwargs = {
            'password': {'write_only': True},  # Don't include password in responses
            'active_status': {'default': 1},
            'place_holder': {'default': 0}
        }
    
    def create(self, validated_data):
        """Create a new user"""
        return User.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing user"""
        instance.name = validated_data.get('name', instance.name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.region = validated_data.get('region', instance.region)
        instance.active_status = validated_data.get('active_status', instance.active_status)
        instance.place_holder = validated_data.get('place_holder', instance.place_holder)
        instance.save()
        return instance

class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (without password)"""
    
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'region', 'active_status', 'place_holder'] 