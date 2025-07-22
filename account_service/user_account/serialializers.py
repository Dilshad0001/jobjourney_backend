from rest_framework import serializers
from .models import CustomUser
import random



# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=CustomUser
#         fields=['email']

#     def create(self, validated_data):
#         try:
#             user=CustomUser.objects.get(email=validated_data.get('email'))
#         except:
#             user=CustomUser.objects.create_user(**validated_data)
#         return user
    

class RequestOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()    

class customuserserializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser    
        fields='__all__'