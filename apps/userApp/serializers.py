
import re
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Users


class usersSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Users
        fields = '__all__'
  
    #----- custome function to hash password becouse the default one is not working
    def create(self, validated_data):
        #phone_number = validated_data.get("phone")
        #phone_pattern = r"^\+\d{1,4}"
        #if not re.match(phone_pattern, phone_number):
        #    raise serializers.ValidationError("phone_number must have country code")
        password = validated_data.pop('password')
        hashed_password = make_password(password)
        instance = super().create(validated_data)
        instance.password = hashed_password
        instance.save()
        return instance
